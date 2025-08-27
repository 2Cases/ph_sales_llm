"""
System prompts and templates for the pharmacy sales chatbot.
Contains all LLM prompts and conversation templates.
"""

# Base system prompt for the sales chatbot
SYSTEM_PROMPT = """You are a professional sales representative for Pharmesol, a pharmaceutical distribution company specializing in supporting high-volume pharmacies. You are handling inbound calls from pharmacies.

    Your role is to:
    1. Be friendly, professional, and helpful
    2. Gather relevant information about the pharmacy
    3. Highlight how Pharmesol can support high Rx volume pharmacies
    4. Offer appropriate follow-up actions (email, callback scheduling)

    Key talking points about Pharmesol:
    - We specialize in supporting high-volume pharmacies
    - We offer competitive pricing and reliable supply chain
    - We provide dedicated account management for established partners
    - We have experience with complex inventory management
    - We offer flexible delivery schedules and emergency supplies

    Guidelines:
    - Keep responses conversational and natural
    - Don't be overly pushy or salesy
    - Focus on understanding their needs first
    - Use the pharmacy data when available to personalize the conversation
    - Always offer concrete next steps (email follow-up or callback scheduling)
    - Be understanding if they're busy and offer alternatives
    - If a customer wants information sent via email, ALWAYS ask for their email address if you don't have it
    - If a customer wants a callback, ALWAYS confirm their phone number and preferred time
    - Collect contact information (email, phone, name) naturally during the conversation

    Available actions you can suggest:
    - send_email: To send detailed information via email
    - schedule_callback: To schedule a more detailed conversation
    - log_lead_information: To save their information for future reference
    - create_follow_up_task: To create internal follow-up tasks
    """

# Template for known pharmacy greeting
KNOWN_PHARMACY_TEMPLATE = """Great! I see you're calling from {pharmacy_name}{location_info}. {rx_volume_info}

    How can Pharmesol help you today? We specialize in supporting pharmacies like yours with reliable supply chain solutions and competitive pricing."""

# Template for unknown pharmacy greeting
UNKNOWN_PHARMACY_TEMPLATE = """Thank you for calling Pharmesol! I don't have your information in our system yet. 

    Could you please tell me:
    1. Your pharmacy name
    2. Your location
    3. Approximately how many prescriptions you fill per month

    This will help me understand how we can best support your pharmacy's needs."""

# Template for Rx volume messaging
RX_VOLUME_MESSAGES = {
    "high": "With your high prescription volume, you'd be an excellent fit for our premium tier services, including dedicated account management and priority inventory allocation.",
    "medium": "Your prescription volume puts you in a great position to benefit from our bulk pricing and reliable delivery schedules.",
    "low": "Even with your current volume, we can offer competitive pricing and room to grow with our flexible service options.",
    "unknown": "Understanding your prescription volume helps us tailor our services to your specific needs."
}

# Email templates
EMAIL_TEMPLATES = {
    "new_lead": {
        "subject": "Thank you for your interest in Pharmesol - {pharmacy_name}",
        "body": """Dear {contact_name},

    Thank you for speaking with us today about Pharmesol's pharmacy distribution services.

    Based on our conversation, here's what we can offer {pharmacy_name}:

    • Competitive pricing on pharmaceutical products
    • Reliable supply chain with consistent inventory
    • Flexible delivery schedules to meet your needs
    • Dedicated customer support
    {rx_volume_benefits}

    I'll be following up with you within the next few business days to discuss how we can support your pharmacy's success.

    In the meantime, please don't hesitate to reach out if you have any questions.

    Best regards,
    Pharmesol Sales Team
    Phone: (555) 123-4567
    Email: sales@pharmesol.com
    """
        },
        "existing_pharmacy": {
            "subject": "Following up on your call - {pharmacy_name}",
            "body": """Dear {contact_name},

    Thank you for reaching out to us today. It's always great to hear from {pharmacy_name}.

    Based on our conversation, I'll be preparing some specific information about:
    {discussion_topics}

    I'll have this information ready for our next conversation. {callback_info}

    Thank you for choosing Pharmesol as your distribution partner.

    Best regards,
    Pharmesol Sales Team
    Phone: (555) 123-4567
    Email: sales@pharmesol.com
    """
        }
    }

# Conversation flow prompts
CONVERSATION_PROMPTS = {
    "gather_basic_info": "I'd love to learn more about your pharmacy. Could you share your pharmacy name, location, and approximate monthly prescription volume?",
    
    "discuss_needs": "What are your biggest challenges with your current pharmaceutical distribution? Are you looking for better pricing, more reliable delivery, or expanded inventory options?",
    
    "offer_solutions": "Based on what you've told me, here's how Pharmesol could help your pharmacy:",
    
    "suggest_next_steps": "Would you prefer that I send you detailed information via email, or would you like to schedule a callback to discuss this further?",
    
    "handle_busy_caller": "I understand you're busy running your pharmacy. Would you prefer if I sent you some information via email, or could we schedule a brief callback at a more convenient time?",
    
    "closing": "Thank you for your time today. I look forward to supporting {pharmacy_name}'s continued success."
}

# Response templates for different scenarios
RESPONSE_TEMPLATES = {
    "data_missing": "I notice we're missing some information about your pharmacy. Could you help me fill in the details?",
    
    "api_error": "I'm having trouble accessing our pharmacy database right now, but I'd still love to help you. Let me gather some basic information.",
    
    "high_volume_pitch": "With your high prescription volume, you're exactly the type of pharmacy we love to work with. Our high-volume tier includes dedicated account management and priority inventory allocation.",
    
    "new_pharmacy_welcome": "Welcome to the Pharmesol family! We're excited about the possibility of supporting your pharmacy's growth.",
    
    "callback_confirmation": "Perfect! I'll make sure someone from our team calls you back at {phone_number} {preferred_time}. In the meantime, I'll send you some initial information via email.",
    
    "email_confirmation": "Great! I'll send you detailed information about our services to {email_address}. You should receive it within the next few minutes."
}

def format_location_info(pharmacy_data):
    """Format location information for greeting."""
    if not pharmacy_data:
        return ""
    
    location_parts = []
    if pharmacy_data.get('city'):
        location_parts.append(pharmacy_data['city'])
    if pharmacy_data.get('state'):
        location_parts.append(pharmacy_data['state'])
    
    if location_parts:
        return f" in {', '.join(location_parts)}"
    return ""

def format_rx_volume_info(pharmacy_data):
    """Format Rx volume information for greeting."""
    if not pharmacy_data or not pharmacy_data.get('rxVolume'):
        return "I'd love to learn more about your prescription volume to see how we can best support you."
    
    rx_volume = pharmacy_data['rxVolume']
    if rx_volume >= 10000:
        return RX_VOLUME_MESSAGES["high"]
    elif rx_volume >= 5000:
        return RX_VOLUME_MESSAGES["medium"]
    elif rx_volume >= 1000:
        return RX_VOLUME_MESSAGES["low"]
    else:
        return RX_VOLUME_MESSAGES["unknown"]

def get_rx_volume_benefits(rx_volume):
    """Get specific benefits based on Rx volume."""
    if not rx_volume or rx_volume == 0:
        return "• Scalable solutions that grow with your business"
    
    benefits = []
    if rx_volume >= 10000:
        benefits.extend([
            "• Premium tier pricing with volume discounts",
            "• Dedicated account manager",
            "• Priority inventory allocation",
            "• Emergency delivery services"
        ])
    elif rx_volume >= 5000:
        benefits.extend([
            "• Volume-based pricing tiers",
            "• Flexible delivery scheduling",
            "• Account management support"
        ])
    else:
        benefits.extend([
            "• Competitive pricing structure",
            "• Growth-oriented service options",
            "• Flexible minimum order requirements"
        ])
    
    return "\n".join(benefits)