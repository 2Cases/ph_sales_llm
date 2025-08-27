"""
Clean conversation flow management for the pharmacy sales chatbot.
Separates conversation logic from LLM interactions for better maintainability.
"""

import logging
import re
from typing import Optional, Tuple, List
from core.models import (
    ConversationState, PharmacyData, LeadData, ConversationStatus,
    ConversationMessage, ActionRequest, PharmacyType
)

logger = logging.getLogger(__name__)

class ConversationFlowManager:
    """
    Manages conversation flow, state, and business logic.
    
    This class handles:
    - Conversation state management
    - User input analysis and classification
    - Business logic for pharmacy interactions
    - Action requirement detection
    """
    
    def __init__(self):
        self.state: Optional[ConversationState] = None
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]
        
    def start_conversation(self, phone_number: str, pharmacy_data: Optional[PharmacyData] = None) -> ConversationState:
        """
        Initialize a new conversation session.
        
        Args:
            phone_number: Caller's phone number
            pharmacy_data: Known pharmacy data (if found in database)
            
        Returns:
            New conversation state
        """
        logger.info(f"Starting conversation for {phone_number}")
        
        # Initialize lead data for unknown callers
        lead_data = None if pharmacy_data else LeadData(phone=phone_number)
        
        self.state = ConversationState(
            phone_number=phone_number,
            pharmacy_data=pharmacy_data,
            lead_data=lead_data,
            status=ConversationStatus.ACTIVE
        )
        
        return self.state
    
    def analyze_user_message(self, message: str) -> dict:
        """
        Analyze user message to extract intent and information.
        
        Args:
            message: User's message content
            
        Returns:
            Analysis results with intent, entities, and suggested actions
        """
        if not message:
            return {'intent': 'unclear', 'entities': {}, 'confidence': 0.0}
        
        message_lower = message.lower()
        analysis = {
            'intent': 'general_inquiry',
            'entities': {},
            'confidence': 0.5,
            'suggested_actions': []
        }
        
        # Extract email addresses
        emails = self._extract_emails(message)
        if emails:
            analysis['entities']['email'] = emails[0]
        
        # Detect intents
        if self._is_email_request(message_lower):
            analysis['intent'] = 'request_email'
            analysis['confidence'] = 0.8
            if not emails and not self.state.has_email:
                analysis['suggested_actions'].append('ask_for_email')
        
        elif self._is_callback_request(message_lower):
            analysis['intent'] = 'request_callback'
            analysis['confidence'] = 0.8
            analysis['entities']['preferred_time'] = self._extract_time_preference(message_lower)
        
        elif self._is_pharmacy_introduction(message_lower):
            analysis['intent'] = 'pharmacy_introduction'
            analysis['confidence'] = 0.9
            
            # Extract pharmacy information
            pharmacy_info = self._extract_pharmacy_info(message)
            analysis['entities'].update(pharmacy_info)
        
        elif self._is_pricing_inquiry(message_lower):
            analysis['intent'] = 'pricing_inquiry'
            analysis['confidence'] = 0.7
            
            # Extract volume information
            volume = self._extract_rx_volume(message)
            if volume:
                analysis['entities']['rx_volume'] = volume
        
        elif self._is_greeting(message_lower):
            analysis['intent'] = 'greeting'
            analysis['confidence'] = 0.6
        
        return analysis
    
    def update_lead_data(self, entities: dict):
        """
        Update lead data with extracted information.
        
        Args:
            entities: Dictionary of extracted entities
        """
        if not self.state or not self.state.lead_data:
            return
        
        lead = self.state.lead_data
        
        if 'email' in entities:
            lead.email = entities['email']
        
        if 'pharmacy_name' in entities:
            lead.pharmacy_name = entities['pharmacy_name']
        
        if 'location' in entities:
            lead.location = entities['location']
        
        if 'rx_volume' in entities:
            lead.rx_volume = entities['rx_volume']
        
        if 'contact_person' in entities:
            lead.contact_person = entities['contact_person']
        
        logger.debug(f"Updated lead data: {lead.completion_percentage}% complete")
    
    def determine_response_strategy(self, analysis: dict) -> dict:
        """
        Determine the best response strategy based on message analysis.
        
        Args:
            analysis: Results from analyze_user_message
            
        Returns:
            Response strategy with type, priority actions, and context
        """
        intent = analysis['intent']
        entities = analysis['entities']
        
        strategy = {
            'response_type': 'conversational',
            'priority_actions': [],
            'context_hints': [],
            'personalization_level': 'medium'
        }
        
        if intent == 'request_email':
            if not self.state.has_email:
                strategy['response_type'] = 'ask_for_email'
                strategy['priority_actions'] = ['collect_email']
            else:
                strategy['response_type'] = 'send_email'
                strategy['priority_actions'] = ['send_email']
        
        elif intent == 'request_callback':
            strategy['response_type'] = 'schedule_callback'
            strategy['priority_actions'] = ['schedule_callback']
            if 'preferred_time' in entities:
                strategy['context_hints'].append(f"preferred_time: {entities['preferred_time']}")
        
        elif intent == 'pharmacy_introduction':
            strategy['response_type'] = 'acknowledge_intro'
            strategy['priority_actions'] = ['update_lead_data', 'assess_fit']
            strategy['personalization_level'] = 'high'
        
        elif intent == 'pricing_inquiry':
            strategy['response_type'] = 'pricing_discussion'
            strategy['priority_actions'] = ['assess_volume', 'present_value_prop']
            if self.state and self.state.pharmacy_data:
                strategy['personalization_level'] = 'high'
        
        # Add context based on conversation state
        if self.state:
            if self.state.is_known_pharmacy:
                strategy['context_hints'].append('known_pharmacy')
                strategy['context_hints'].append(f"pharmacy_type: {self.state.pharmacy_data.pharmacy_type.value}")
            else:
                strategy['context_hints'].append('new_lead')
                if self.state.lead_data:
                    strategy['context_hints'].append(f"lead_completeness: {self.state.lead_data.completion_percentage}%")
        
        return strategy
    
    def get_conversation_context(self) -> str:
        """
        Generate context string for LLM with current conversation state.
        
        Returns:
            Formatted context string
        """
        if not self.state:
            return "No active conversation"
        
        context_parts = [
            f"PHONE: {self.state.phone_number}",
            f"STATUS: {self.state.status.value}",
            f"MESSAGES: {len(self.state.messages)}"
        ]
        
        if self.state.is_known_pharmacy:
            pharmacy = self.state.pharmacy_data
            context_parts.extend([
                f"KNOWN PHARMACY: {pharmacy.name}",
                f"LOCATION: {pharmacy.location_display}",
                f"TYPE: {pharmacy.pharmacy_type.value}",
                f"VOLUME: {pharmacy.rx_volume or 'Unknown'}"
            ])
            if pharmacy.email:
                context_parts.append(f"EMAIL: {pharmacy.email}")
        else:
            lead = self.state.lead_data
            context_parts.extend([
                f"NEW LEAD: {lead.pharmacy_name or 'Unknown'}",
                f"COMPLETENESS: {lead.completion_percentage}%"
            ])
            if lead.email:
                context_parts.append(f"EMAIL: {lead.email}")
            if lead.rx_volume:
                context_parts.append(f"VOLUME: {lead.rx_volume}")
        
        return " | ".join(context_parts)
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        emails = []
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text)
            emails.extend(matches)
        return list(set(emails))  # Remove duplicates
    
    def _is_email_request(self, message: str) -> bool:
        """Check if message is requesting email information."""
        keywords = ['email', 'send me', 'mail me', 'information', 'details', 'send']
        return any(keyword in message for keyword in keywords)
    
    def _is_callback_request(self, message: str) -> bool:
        """Check if message is requesting a callback."""
        keywords = ['callback', 'call back', 'call me', 'schedule', 'call', 'phone']
        return any(keyword in message for keyword in keywords)
    
    def _is_pharmacy_introduction(self, message: str) -> bool:
        """Check if message is introducing pharmacy information."""
        indicators = [
            'pharmacy' in message, 'calling from' in message,
            "i'm from" in message, 'located' in message,
            'we fill' in message, 'prescriptions' in message
        ]
        return any(indicators)
    
    def _is_pricing_inquiry(self, message: str) -> bool:
        """Check if message is asking about pricing."""
        keywords = ['pricing', 'price', 'cost', 'rates', 'volume', 'discount', 'competitive']
        return any(keyword in message for keyword in keywords)
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        return any(greeting in message for greeting in greetings)
    
    def _extract_pharmacy_info(self, message: str) -> dict:
        """Extract pharmacy information from message."""
        info = {}
        
        # Extract pharmacy name (simple pattern matching)
        name_patterns = [
            r"calling from ([^,.]+)",
            r"i'm from ([^,.]+)",
            r"at ([^,.]+pharmacy)",
            r"([^,.]*pharmacy[^,.]*)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info['pharmacy_name'] = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r"in ([^,.]+,?\s*[A-Z]{2})",
            r"located in ([^,.]+)",
            r"from ([^,.]+,?\s*[A-Z]{2})"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info['location'] = match.group(1).strip()
                break
        
        return info
    
    def _extract_rx_volume(self, message: str) -> Optional[int]:
        """Extract prescription volume from message."""
        patterns = [
            r"(\d+,?\d*)\s*prescriptions",
            r"(\d+,?\d*)\s*rx",
            r"volume.*?(\d+,?\d*)",
            r"fill.*?(\d+,?\d*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                volume_str = match.group(1).replace(',', '')
                try:
                    return int(volume_str)
                except ValueError:
                    continue
        return None
    
    def _extract_time_preference(self, message: str) -> Optional[str]:
        """Extract time preference from message."""
        time_patterns = [
            'tomorrow morning', 'tomorrow afternoon', 'tomorrow',
            'this afternoon', 'this morning', 'next week',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday'
        ]
        
        for pattern in time_patterns:
            if pattern in message:
                return pattern
        return None