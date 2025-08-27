"""
Main chatbot implementation with clean architecture and separation of concerns.
This is the primary interface that coordinates all components.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from models import ConversationState, PharmacyData
from integration import PharmacyAPIClient, APIError
from conversation_manager import ConversationFlowManager
from action_handler import ActionHandler
from logging_config import setup_logging, DebugContext, monitor_performance
from prompt import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

class PharmacySalesChatbot:
    """
    Main chatbot class with clean architecture and excellent usability.
    
    This class orchestrates all components:
    - API client for pharmacy data
    - Conversation flow management
    - Action execution
    - LLM interactions
    - Comprehensive logging
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        log_level: str = "INFO",
        enable_debug: bool = False
    ):
        """
        Initialize the chatbot with all necessary components.
        
        Args:
            openai_api_key: OpenAI API key (uses env var if not provided)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable_debug: Enable detailed debug logging
        """
        
        # Set up logging first
        self.debug_mode = enable_debug
        log_level = "DEBUG" if enable_debug else log_level
        self.logger = setup_logging(level=log_level)
        
        # Initialize conversation ID for this session
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.set_conversation_id(self.conversation_id)
        
        with DebugContext("chatbot_initialization") as debug:
            # Initialize OpenAI client
            self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                    "or pass openai_api_key parameter."
                )
            
            self.llm_client = OpenAI(api_key=self.openai_api_key)
            debug.log_step("OpenAI client initialized")
            
            # Initialize components
            self.api_client = PharmacyAPIClient()
            self.conversation_manager = ConversationFlowManager()
            self.action_handler = ActionHandler()
            
            debug.log_step("All components initialized")
            
            # Test API connectivity
            if self.api_client.health_check():
                debug.log_step("API health check passed")
            else:
                debug.log_step("API health check failed - continuing with degraded functionality")
        
        self.logger.logger.info(f"🤖 Chatbot initialized | Conversation ID: {self.conversation_id}")
    
    @monitor_performance
    def start_conversation(self, phone_number: str) -> str:
        """
        Start a new conversation session.
        
        Args:
            phone_number: Caller's phone number
            
        Returns:
            Initial greeting message
        """
        
        with DebugContext("conversation_start") as debug:
            debug.log_step("Looking up pharmacy data")
            
            # Look up pharmacy information
            pharmacy_data = None
            try:
                raw_pharmacy_data = self.api_client.find_pharmacy_by_phone(phone_number)
                if raw_pharmacy_data:
                    # Convert dictionary to PharmacyData object
                    pharmacy_data = PharmacyData.from_api_response(raw_pharmacy_data)
                self.logger.log_api_call("find_pharmacy_by_phone", success=True)
            except APIError as e:
                self.logger.log_api_call("find_pharmacy_by_phone", success=False)
                debug.log_step(f"API lookup failed: {e}")
            except Exception as e:
                self.logger.log_api_call("find_pharmacy_by_phone", success=False)
                debug.log_step(f"Data conversion failed: {e}")
            
            # Initialize conversation state
            self.conversation_state = self.conversation_manager.start_conversation(
                phone_number, pharmacy_data
            )
            
            debug.log_checkpoint(
                "conversation_initialized",
                {
                    'is_known_pharmacy': pharmacy_data is not None,
                    'pharmacy_name': pharmacy_data.name if pharmacy_data else 'Unknown'
                }
            )
            
            # Generate initial greeting
            greeting = self._generate_greeting(pharmacy_data)
            self.conversation_state.add_message("assistant", greeting)
            
            # Log conversation start
            self.logger.log_conversation_start(phone_number, pharmacy_data is not None)
            self.logger.log_bot_response(greeting, {'response_type': 'greeting'})
            
        return greeting
    
    @monitor_performance
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and generate appropriate response.
        
        Args:
            user_message: User's input message
            
        Returns:
            Chatbot response
        """
        
        if not hasattr(self, 'conversation_state'):
            raise RuntimeError("Conversation not started. Call start_conversation() first.")
        
        with DebugContext("message_processing") as debug:
            # Add user message to conversation
            self.conversation_state.add_message("user", user_message)
            
            # Analyze user message
            debug.log_step("Analyzing user message")
            analysis = self.conversation_manager.analyze_user_message(user_message)
            
            self.logger.log_user_message(user_message, analysis)
            debug.log_checkpoint("message_analyzed", {'intent': analysis['intent']})
            
            # Update lead data if applicable
            if analysis['entities'] and self.conversation_state.lead_data:
                self.conversation_manager.update_lead_data(analysis['entities'])
                debug.log_step("Lead data updated")
            
            # Determine response strategy
            debug.log_step("Determining response strategy")
            strategy = self.conversation_manager.determine_response_strategy(analysis)
            
            # Handle immediate actions if needed
            response = self._handle_message_with_strategy(analysis, strategy, debug)
            
            # Add response to conversation
            self.conversation_state.add_message("assistant", response)
            self.logger.log_bot_response(response, strategy)
            
        return response
    
    def _handle_message_with_strategy(
        self, 
        analysis: Dict[str, Any], 
        strategy: Dict[str, Any],
        debug: DebugContext
    ) -> str:
        """Handle message processing based on determined strategy."""
        
        intent = analysis['intent']
        entities = analysis['entities']
        response_type = strategy['response_type']
        
        debug.log_step(f"Handling {response_type} response")
        
        # Handle direct actions
        if response_type == 'ask_for_email':
            result = self.action_handler.execute_action(
                'ask_for_email', 
                self.conversation_state
            )
            return result.message
        
        elif response_type == 'send_email':
            # Execute email sending
            email_result = self.action_handler.execute_action(
                'send_email',
                self.conversation_state,
                email=entities.get('email')
            )
            
            self.logger.log_action_execution('send_email', email_result.success, email_result.data)
            
            if email_result.success:
                # Log lead if it's a new one
                if not self.conversation_state.is_known_pharmacy:
                    self.action_handler.execute_action('log_lead', self.conversation_state)
                
                return email_result.message
            else:
                return "I apologize, but I'm having trouble sending the email right now. Could you please provide your email address again?"
        
        elif response_type == 'schedule_callback':
            callback_result = self.action_handler.execute_action(
                'schedule_callback',
                self.conversation_state,
                preferred_time=entities.get('preferred_time')
            )
            
            self.logger.log_action_execution('schedule_callback', callback_result.success, callback_result.data)
            return callback_result.message
        
        # For conversational responses, use LLM
        else:
            return self._generate_llm_response(strategy, debug)
    
    @monitor_performance
    def _generate_llm_response(self, strategy: Dict[str, Any], debug: DebugContext) -> str:
        """Generate response using LLM with context."""
        
        try:
            debug.log_step("Preparing LLM context")
            
            # Prepare system message with strategy context
            context = self.conversation_manager.get_conversation_context()
            strategy_hints = " | ".join(strategy.get('context_hints', []))
            
            enhanced_system_prompt = f"""{SYSTEM_PROMPT}

CURRENT CONTEXT:
{context}

RESPONSE STRATEGY:
- Type: {strategy['response_type']}
- Personalization: {strategy['personalization_level']}
- Context: {strategy_hints}
- Priority Actions: {', '.join(strategy.get('priority_actions', []))}

INSTRUCTIONS:
- Use the context above to personalize your response
- Be natural and conversational
- If asking for information, explain why it's helpful
- Always offer next steps (email or callback)
"""
            
            # Prepare conversation history for LLM
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            
            # Add recent conversation history (last 6 messages to stay within context limits)
            recent_messages = self.conversation_state.messages[-6:]
            for msg in recent_messages:
                messages.append({"role": msg.role, "content": msg.content})
            
            debug.log_step("Calling LLM API")
            
            # Make LLM API call
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content.strip()
            
            # Log LLM usage
            tokens_used = response.usage.total_tokens if response.usage else None
            self.logger.log_llm_call("gpt-3.5-turbo", tokens_used, True)
            
            debug.log_step("LLM response generated successfully")
            return llm_response
            
        except Exception as e:
            self.logger.log_llm_call("gpt-3.5-turbo", None, False)
            debug.log_step(f"LLM call failed: {e}")
            
            # Fallback response
            return self._generate_fallback_response()
    
    def _generate_greeting(self, pharmacy_data: Optional[PharmacyData]) -> str:
        """Generate initial greeting based on pharmacy data."""
        
        if pharmacy_data:
            # Known pharmacy greeting
            location_info = f" in {pharmacy_data.location_display}" if pharmacy_data.city else ""
            
            volume_info = ""
            if pharmacy_data.rx_volume:
                if pharmacy_data.rx_volume >= 10000:
                    volume_info = " With your high prescription volume, you'd be an excellent fit for our premium tier services."
                elif pharmacy_data.rx_volume >= 5000:
                    volume_info = " Your prescription volume puts you in a great position to benefit from our bulk pricing."
                else:
                    volume_info = " We can offer competitive pricing and room to grow with our flexible service options."
            
            return f"Great! I see you're calling from {pharmacy_data.name}{location_info}.{volume_info} How can Pharmesol help you today?"
        
        else:
            # New lead greeting
            return """Thank you for calling Pharmesol! I don't have your information in our system yet.

Could you please tell me:
1. Your pharmacy name
2. Your location  
3. Approximately how many prescriptions you fill per month

This will help me understand how we can best support your pharmacy's needs."""
    
    def _generate_fallback_response(self) -> str:
        """Generate fallback response when LLM is unavailable."""
        
        if not self.conversation_state.has_email:
            return "I'd be happy to help you with information about Pharmesol's services. Could you please provide your email address so I can send you detailed information?"
        else:
            return "Thank you for your interest in Pharmesol. Let me connect you with one of our specialists who can provide detailed information about our services. Would you prefer a callback or email follow-up?"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get comprehensive conversation summary."""
        
        if not hasattr(self, 'conversation_state'):
            return {'status': 'not_started'}
        
        state = self.conversation_state
        
        summary = {
            'conversation_id': self.conversation_id,
            'phone_number': state.phone_number,
            'status': state.status.value,
            'message_count': len(state.messages),
            'actions_taken': state.actions_taken.copy(),
            'is_known_pharmacy': state.is_known_pharmacy,
            'has_email': state.has_email,
            'started_at': state.started_at.isoformat(),
        }
        
        if state.pharmacy_data:
            summary['pharmacy_data'] = {
                'name': state.pharmacy_data.name,
                'location': state.pharmacy_data.location_display,
                'type': state.pharmacy_data.pharmacy_type.value,
                'volume': state.pharmacy_data.rx_volume
            }
        
        if state.lead_data:
            summary['lead_data'] = {
                'pharmacy_name': state.lead_data.pharmacy_name,
                'completion_percentage': state.lead_data.completion_percentage,
                'has_email': bool(state.lead_data.email),
                'estimated_volume': state.lead_data.rx_volume
            }
        
        # Add action handler summary
        summary['action_summary'] = self.action_handler.get_action_summary()
        
        return summary
    
    def end_conversation(self) -> str:
        """End conversation with appropriate closing."""
        
        if not hasattr(self, 'conversation_state'):
            return "Thank you for your interest in Pharmesol!"
        
        pharmacy_name = self.conversation_state.current_pharmacy_name
        closing = f"Thank you for your time today. I look forward to supporting {pharmacy_name}'s continued success with Pharmesol's reliable distribution services."
        
        # Log conversation end
        self.logger.logger.info(f"🏁 CONVERSATION END | Summary: {len(self.conversation_state.messages)} messages, {len(self.conversation_state.actions_taken)} actions")
        
        return closing
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if hasattr(self, 'api_client'):
            self.api_client.close()
        
        if exc_type:
            self.logger.logger.error(f"💥 Chatbot session ended with error: {exc_type.__name__}: {exc_val}")
        else:
            self.logger.logger.info("✨ Chatbot session ended successfully")