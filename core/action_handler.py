"""
Clean action handling system for chatbot operations.
Provides structured, testable, and maintainable action execution.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from core.models import ConversationState, PharmacyType
from utils.function_calls import send_email, schedule_callback, log_lead_information, create_follow_up_task

logger = logging.getLogger(__name__)

class ActionResult:
    """Result of an action execution."""
    
    def __init__(self, success: bool, message: str, data: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __bool__(self):
        return self.success

class ActionHandler:
    """
    Handles all business actions for the chatbot.
    
    Provides clean separation between conversation logic and action execution,
    making the system more testable and maintainable.
    """
    
    def __init__(self):
        self.action_history = []
    
    def execute_action(self, action_type: str, state: ConversationState, **kwargs) -> ActionResult:
        """
        Execute a specific action based on type.
        
        Args:
            action_type: Type of action to execute
            state: Current conversation state
            **kwargs: Additional parameters for the action
            
        Returns:
            ActionResult indicating success/failure and details
        """
        logger.info(f"Executing action: {action_type}")
        
        action_map = {
            'send_email': self._handle_send_email,
            'schedule_callback': self._handle_schedule_callback,
            'log_lead': self._handle_log_lead,
            'create_follow_up': self._handle_create_follow_up,
            'ask_for_email': self._handle_ask_for_email,
            'ask_for_callback_details': self._handle_ask_for_callback_details
        }
        
        if action_type not in action_map:
            return ActionResult(
                success=False,
                message=f"Unknown action type: {action_type}"
            )
        
        try:
            result = action_map[action_type](state, **kwargs)
            self.action_history.append({
                'action': action_type,
                'timestamp': datetime.now(),
                'success': result.success,
                'details': result.data
            })
            
            if result.success:
                state.add_action(action_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Action {action_type} failed: {e}")
            return ActionResult(
                success=False,
                message=f"Action failed: {str(e)}"
            )
    
    def _handle_send_email(self, state: ConversationState, **kwargs) -> ActionResult:
        """Handle sending email with pharmacy information."""
        
        # Determine email address
        email = kwargs.get('email') or state.email_address
        if not email:
            return ActionResult(
                success=False,
                message="No email address available"
            )
        
        # Prepare email content based on pharmacy type
        if state.is_known_pharmacy:
            subject, body = self._prepare_existing_pharmacy_email(state)
        else:
            subject, body = self._prepare_new_lead_email(state)
        
        # Send email using mock function
        try:
            success = send_email(email, subject, body)
            
            if success:
                return ActionResult(
                    success=True,
                    message=f"Email sent successfully to {email}",
                    data={'email': email, 'subject': subject}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Email sending failed"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Email error: {str(e)}"
            )
    
    def _handle_schedule_callback(self, state: ConversationState, **kwargs) -> ActionResult:
        """Handle callback scheduling."""
        
        preferred_time = kwargs.get('preferred_time', 'during business hours')
        contact_name = state.current_pharmacy_name
        notes = self._generate_callback_notes(state)
        
        try:
            callback_details = schedule_callback(
                phone_number=state.phone_number,
                preferred_time=preferred_time,
                contact_name=contact_name,
                notes=notes
            )
            
            # Create follow-up task
            self._handle_create_follow_up(state, task_type='callback_follow_up')
            
            return ActionResult(
                success=True,
                message=f"Callback scheduled for {preferred_time}",
                data=callback_details
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Callback scheduling failed: {str(e)}"
            )
    
    def _handle_log_lead(self, state: ConversationState, **kwargs) -> ActionResult:
        """Handle logging new lead information."""
        
        if not state.lead_data:
            return ActionResult(
                success=False,
                message="No lead data to log"
            )
        
        try:
            lead_dict = {
                'pharmacy_name': state.lead_data.pharmacy_name or 'Unknown',
                'phone': state.lead_data.phone,
                'email': state.lead_data.email,
                'location': state.lead_data.location,
                'rx_volume': state.lead_data.rx_volume,
                'contact_person': state.lead_data.contact_person,
                'completion_percentage': state.lead_data.completion_percentage,
                'interests': ', '.join(state.lead_data.interests) if state.lead_data.interests else '',
                'notes': state.lead_data.notes
            }
            
            success = log_lead_information(lead_dict)
            
            if success:
                return ActionResult(
                    success=True,
                    message="Lead information logged successfully",
                    data={'lead_id': f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Lead logging failed"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Lead logging error: {str(e)}"
            )
    
    def _handle_create_follow_up(self, state: ConversationState, **kwargs) -> ActionResult:
        """Handle creating follow-up tasks."""
        
        task_type = kwargs.get('task_type', 'general_follow_up')
        contact_info = {
            'phone': state.phone_number,
            'email': state.email_address
        }
        
        try:
            task_details = create_follow_up_task(
                pharmacy_name=state.current_pharmacy_name,
                contact_info=contact_info,
                task_type=task_type
            )
            
            return ActionResult(
                success=True,
                message="Follow-up task created",
                data=task_details
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Follow-up task creation failed: {str(e)}"
            )
    
    def _handle_ask_for_email(self, state: ConversationState, **kwargs) -> ActionResult:
        """Generate response asking for email address."""
        
        pharmacy_name = state.current_pharmacy_name
        
        messages = [
            f"I'd be happy to send you detailed information about our services! Could you please provide your email address so I can send you everything {pharmacy_name} needs to know about Pharmesol?",
            "To send you our comprehensive service information, I'll need your email address. What's the best email to reach you at?",
            "I'd love to get you all the details about how Pharmesol can support your pharmacy. What email address should I send the information to?"
        ]
        
        # Choose message based on conversation context
        message = messages[0]  # Default
        if len(state.messages) > 3:
            message = messages[1]  # Slightly different for longer conversations
        
        return ActionResult(
            success=True,
            message=message,
            data={'action_required': 'collect_email'}
        )
    
    def _handle_ask_for_callback_details(self, state: ConversationState, **kwargs) -> ActionResult:
        """Generate response asking for callback details."""
        
        message = "I'd be happy to schedule a callback for you! What time works best - would you prefer morning or afternoon, and which day this week?"
        
        return ActionResult(
            success=True,
            message=message,
            data={'action_required': 'collect_callback_details'}
        )
    
    def _prepare_existing_pharmacy_email(self, state: ConversationState) -> tuple:
        """Prepare email for existing pharmacy."""
        
        pharmacy = state.pharmacy_data
        subject = f"Following up on your call - {pharmacy.name}"
        
        volume_benefits = self._get_volume_benefits(pharmacy.pharmacy_type)
        
        body = f"""Dear {pharmacy.contact_person or 'there'},

        Thank you for reaching out to us today. It's always great to hear from {pharmacy.name}.

        Based on our conversation and your {pharmacy.rx_volume or 'significant'} monthly prescription volume, here's how Pharmesol can specifically support your pharmacy:

        {volume_benefits}

        Our team understands the unique challenges facing pharmacies in {pharmacy.location_display}, and we're committed to providing solutions that help you serve your community better.

        I'll be preparing detailed pricing information tailored to your volume and will follow up within the next business day.

        Thank you for considering Pharmesol as your distribution partner.

        Best regards,
        Pharmesol Sales Team
        Phone: (555) 123-4567
        Email: sales@pharmesol.com"""

        return subject, body
    
    def _prepare_new_lead_email(self, state: ConversationState) -> tuple:
        """Prepare email for new lead."""
        
        lead = state.lead_data
        pharmacy_name = lead.pharmacy_name or 'your pharmacy'
        subject = f"Welcome to Pharmesol - {pharmacy_name}"
        
        # Determine benefits based on known volume
        if lead.rx_volume:
            if lead.rx_volume >= 10000:
                volume_benefits = self._get_volume_benefits(PharmacyType.HIGH_VOLUME)
            elif lead.rx_volume >= 5000:
                volume_benefits = self._get_volume_benefits(PharmacyType.MEDIUM_VOLUME)
            else:
                volume_benefits = self._get_volume_benefits(PharmacyType.LOW_VOLUME)
        else:
            volume_benefits = self._get_volume_benefits(PharmacyType.STARTUP)
        
        body = f"""Dear {lead.contact_person or 'there'},

        Thank you for your interest in Pharmesol's pharmaceutical distribution services.

        Based on our conversation about {pharmacy_name}, here's what we can offer:

        {volume_benefits}

        We're excited about the opportunity to support {pharmacy_name}'s success and help you better serve your community.

        Our team will follow up within the next few business days to discuss specific pricing and service details tailored to your needs.

        Best regards,
        Pharmesol Sales Team
        Phone: (555) 123-4567
        Email: sales@pharmesol.com"""

        return subject, body
    
    def _get_volume_benefits(self, pharmacy_type: PharmacyType) -> str:
        """Get benefits text based on pharmacy type."""
        
        benefits_map = {
            PharmacyType.HIGH_VOLUME: """• Premium tier pricing with significant volume discounts
            • Dedicated account manager for personalized service
            • Priority inventory allocation and emergency delivery
            • Advanced inventory management tools and reporting
            • Flexible payment terms and credit options""",
            
            PharmacyType.MEDIUM_VOLUME: """• Volume-based pricing tiers with competitive rates
            • Reliable delivery scheduling (2-3 times per week)
            • Account management support and regular check-ins
            • Inventory optimization assistance
            • Emergency delivery services when needed""",
            
            PharmacyType.LOW_VOLUME: """• Competitive pricing structure designed for growing pharmacies
            • Flexible delivery options (weekly or bi-weekly)
            • Growth-oriented service packages
            • Inventory management support
            • No minimum order requirements to start""",
            
            PharmacyType.STARTUP: """• Startup-friendly pricing with room to grow
            • Flexible minimum order requirements
            • Business development support and guidance
            • Scalable solutions that adapt to your growth
            • Educational resources for pharmacy operations"""
        }
        
        return benefits_map.get(pharmacy_type, benefits_map[PharmacyType.STARTUP])
    
    def _generate_callback_notes(self, state: ConversationState) -> str:
        """Generate notes for callback scheduling."""
        
        notes_parts = []
        
        if state.is_known_pharmacy:
            pharmacy = state.pharmacy_data
            notes_parts.append(f"Existing pharmacy: {pharmacy.name}")
            if pharmacy.rx_volume:
                notes_parts.append(f"Volume: {pharmacy.rx_volume}/month")
        else:
            lead = state.lead_data
            notes_parts.append(f"New lead: {lead.pharmacy_name or 'TBD'}")
            if lead.rx_volume:
                notes_parts.append(f"Estimated volume: {lead.rx_volume}/month")
            notes_parts.append(f"Lead completeness: {lead.completion_percentage}%")
        
        notes_parts.append(f"Conversation length: {len(state.messages)} messages")
        notes_parts.append(f"Actions taken: {', '.join(state.actions_taken) if state.actions_taken else 'None'}")
        
        return " | ".join(notes_parts)
    
    def get_action_summary(self) -> Dict[str, Any]:
        """Get summary of all actions taken."""
        
        total_actions = len(self.action_history)
        successful_actions = sum(1 for action in self.action_history if action['success'])
        
        action_types = {}
        for action in self.action_history:
            action_type = action['action']
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'success_rate': successful_actions / total_actions if total_actions > 0 else 0,
            'action_types': action_types,
            'recent_actions': self.action_history[-5:] if self.action_history else []
        }