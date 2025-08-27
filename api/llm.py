"""
LLM interaction module for the pharmacy sales chatbot.
Handles conversation flow and LLM API calls.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from utils.prompt import (
    SYSTEM_PROMPT, KNOWN_PHARMACY_TEMPLATE, UNKNOWN_PHARMACY_TEMPLATE,
    format_location_info, format_rx_volume_info, CONVERSATION_PROMPTS,
    EMAIL_TEMPLATES, get_rx_volume_benefits
)
from utils.function_calls import send_email, schedule_callback, log_lead_information, create_follow_up_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PharmacyChatbot:
    """Main chatbot class handling LLM interactions and conversation flow."""
    
    def __init__(self, openai_api_key: str = None):
        """
        Initialize the chatbot with OpenAI API key.
        
        Args:
            openai_api_key: OpenAI API key, will use environment variable if not provided
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Get model from environment variable
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.pharmacy_data = None
        self.lead_data = {}
        
    def start_conversation(self, phone_number: str, pharmacy_data: Optional[Dict] = None) -> str:
        """
        Start a new conversation with initial greeting.
        
        Args:
            phone_number: Caller's phone number
            pharmacy_data: Pharmacy information from API lookup (if found)
            
        Returns:
            Initial greeting message
        """
        self.phone_number = phone_number
        self.pharmacy_data = pharmacy_data
        self.conversation_history = []
        
        # Create initial greeting based on whether pharmacy is known
        if pharmacy_data:
            greeting = self._create_known_pharmacy_greeting(pharmacy_data)
        else:
            greeting = self._create_unknown_pharmacy_greeting()
        
        # Add greeting to conversation history
        self.conversation_history.append({"role": "assistant", "content": greeting})
        
        return greeting
    
    def _create_known_pharmacy_greeting(self, pharmacy_data: Dict) -> str:
        """Create greeting for known pharmacy."""
        pharmacy_name = pharmacy_data.get('name', 'your pharmacy')
        location_info = format_location_info(pharmacy_data)
        rx_volume_info = format_rx_volume_info(pharmacy_data)
        
        return KNOWN_PHARMACY_TEMPLATE.format(
            pharmacy_name=pharmacy_name,
            location_info=location_info,
            rx_volume_info=rx_volume_info
        )
    
    def _create_unknown_pharmacy_greeting(self) -> str:
        """Create greeting for unknown pharmacy."""
        return UNKNOWN_PHARMACY_TEMPLATE
    
    def process_user_message(self, user_message: str) -> str:
        """
        Process user message and generate appropriate response.
        
        Args:
            user_message: Message from the user
            
        Returns:
            Chatbot response
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Check if user is requesting specific actions
        if self._is_requesting_email(user_message):
            return self._handle_email_request(user_message)
        elif self._is_requesting_callback(user_message):
            return self._handle_callback_request(user_message)
        elif self._contains_contact_info(user_message):
            self._extract_lead_information(user_message)
        
        # Generate response using LLM
        response = self._generate_llm_response()
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _generate_llm_response(self) -> str:
        """Generate response using OpenAI LLM."""
        try:
            # Prepare system message with context
            system_message = self._prepare_system_message()
            
            # Prepare messages for LLM
            messages = [{"role": "system", "content": system_message}] + self.conversation_history
            
            # Make LLM API call
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return "I apologize, but I'm experiencing some technical difficulties. Let me take down your information manually and have someone from our team reach out to you."
    
    def _prepare_system_message(self) -> str:
        """Prepare system message with current context."""
        context_info = []
        
        if self.pharmacy_data:
            context_info.append(f"KNOWN PHARMACY DATA: {self.pharmacy_data}")
        
        if self.lead_data:
            context_info.append(f"COLLECTED LEAD DATA: {self.lead_data}")
        
        context_info.append(f"CALLER PHONE NUMBER: {self.phone_number}")
        
        context = "\n".join(context_info) if context_info else ""
        
        return f"{SYSTEM_PROMPT}\n\nCURRENT CONTEXT:\n{context}"
    
    def _is_requesting_email(self, message: str) -> bool:
        """Check if user is requesting email information."""
        email_keywords = ['email', 'send me', 'mail me', 'information', 'details']
        # Check for email request keywords OR if an email address is provided
        has_email_keywords = any(keyword in message.lower() for keyword in email_keywords)
        has_email_address = '@' in message
        # Return True if requesting email info, regardless of whether email is provided in same message
        return has_email_keywords or has_email_address
    
    def _is_requesting_callback(self, message: str) -> bool:
        """Check if user is requesting a callback."""
        callback_keywords = ['callback', 'call back', 'call me', 'schedule', 'later']
        return any(keyword in message.lower() for keyword in callback_keywords)
    
    def _contains_contact_info(self, message: str) -> bool:
        """Check if message contains contact information."""
        return '@' in message or any(char.isdigit() for char in message)
    
    def _extract_lead_information(self, message: str) -> None:
        """Extract and store lead information from user message."""
        # Simple extraction - in production, you'd use NLP/regex for better extraction
        words = message.split()
        
        # Look for email
        for word in words:
            if '@' in word and '.' in word:
                self.lead_data['email'] = word
        
        # Look for pharmacy name patterns
        if 'pharmacy' in message.lower() or 'drug' in message.lower():
            # Extract potential pharmacy name
            for i, word in enumerate(words):
                if word.lower() in ['pharmacy', 'drug', 'store']:
                    if i > 0:
                        self.lead_data['pharmacy_name'] = ' '.join(words[max(0, i-2):i+1])
        
        # Look for location info
        if 'located' in message.lower() or 'in ' in message.lower():
            # Extract potential location
            words_lower = [w.lower() for w in words]
            if 'in' in words_lower:
                idx = words_lower.index('in')
                if idx + 1 < len(words):
                    self.lead_data['location'] = words[idx + 1]
    
    def _handle_email_request(self, message: str) -> str:
        """Handle email information request."""
        # First, try to extract email from current message
        words = message.split()
        email = None
        for word in words:
            if '@' in word and '.' in word:
                email = word
                break
        
        # If no email in current message, check if we have one stored from previous messages
        if not email and self.lead_data.get('email'):
            email = self.lead_data['email']
        
        # If still no email, ask for it
        if not email:
            return "I'd be happy to send you information! Could you please provide your email address?"
        
        # Determine email template based on pharmacy status
        if self.pharmacy_data:
            template = EMAIL_TEMPLATES['existing_pharmacy']
            pharmacy_name = self.pharmacy_data.get('name', 'your pharmacy')
            contact_name = self.lead_data.get('contact_name', 'there')
        else:
            template = EMAIL_TEMPLATES['new_lead']
            pharmacy_name = self.lead_data.get('pharmacy_name', 'your pharmacy')
            contact_name = self.lead_data.get('contact_name', 'there')
        
        # Prepare email content
        rx_volume = self.pharmacy_data.get('rxVolume') if self.pharmacy_data else self.lead_data.get('rx_volume', 0)
        rx_volume_benefits = get_rx_volume_benefits(rx_volume)
        
        subject = template['subject'].format(pharmacy_name=pharmacy_name)
        body = template['body'].format(
            contact_name=contact_name,
            pharmacy_name=pharmacy_name,
            rx_volume_benefits=rx_volume_benefits,
            discussion_topics="• Pricing and service options\n• Delivery scheduling\n• Account setup process",
            callback_info="I'll also give you a call tomorrow to make sure you received everything."
        )
        
        # Send email using mock function
        send_email(email, subject, body)
        
        # Log the lead if new
        if not self.pharmacy_data:
            self.lead_data['email'] = email
            log_lead_information(self.lead_data)
        
        return f"Perfect! I've sent detailed information about Pharmesol's services to {email}. You should receive it within the next few minutes."
    
    def _handle_callback_request(self, message: str) -> str:
        """Handle callback scheduling request."""
        # Extract preferred time if mentioned
        preferred_time = "during business hours"
        if "tomorrow" in message.lower():
            preferred_time = "tomorrow during business hours"
        elif "afternoon" in message.lower():
            preferred_time = "this afternoon"
        elif "morning" in message.lower():
            preferred_time = "tomorrow morning"
        
        # Get contact name
        contact_name = "there"
        if self.pharmacy_data:
            contact_name = self.pharmacy_data.get('name', 'your pharmacy')
        elif self.lead_data.get('pharmacy_name'):
            contact_name = self.lead_data['pharmacy_name']
        
        # Schedule callback using mock function
        callback_details = schedule_callback(
            phone_number=self.phone_number,
            preferred_time=preferred_time,
            contact_name=contact_name,
            notes=f"Interested in Pharmesol services. Conversation context: {len(self.conversation_history)} messages exchanged."
        )
        
        # Create follow-up task
        contact_info = {"phone": self.phone_number}
        if self.lead_data.get('email'):
            contact_info['email'] = self.lead_data['email']
        
        create_follow_up_task(contact_name, contact_info, "callback_follow_up")
        
        return f"Excellent! I've scheduled a callback for you {preferred_time} at {self.phone_number}. One of our senior sales representatives will call you to discuss how we can support your pharmacy's needs."
    
    def end_conversation(self) -> str:
        """End the conversation with appropriate closing."""
        if self.pharmacy_data:
            pharmacy_name = self.pharmacy_data.get('name', 'your pharmacy')
        else:
            pharmacy_name = self.lead_data.get('pharmacy_name', 'your pharmacy')
        
        closing = CONVERSATION_PROMPTS['closing'].format(pharmacy_name=pharmacy_name)
        self.conversation_history.append({"role": "assistant", "content": closing})
        
        return closing
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation for logging purposes."""
        return {
            "phone_number": self.phone_number,
            "pharmacy_data": self.pharmacy_data,
            "lead_data": self.lead_data,
            "conversation_length": len(self.conversation_history),
            "actions_taken": self._get_actions_taken()
        }
    
    def _get_actions_taken(self) -> List[str]:
        """Get list of actions taken during conversation."""
        actions = []
        
        for message in self.conversation_history:
            if message["role"] == "assistant":
                content = message["content"].lower()
                if "sent detailed information" in content or "email" in content:
                    actions.append("email_sent")
                if "scheduled a callback" in content or "callback" in content:
                    actions.append("callback_scheduled")
        
        return actions