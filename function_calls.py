"""
Mock utility functions for pharmacy sales chatbot.
These functions simulate real-world actions like sending emails and scheduling callbacks.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(recipient_email: str, subject: str, body: str, sender: str = "sales@pharmesol.com") -> bool:
    """
    Mock function to simulate sending an email.
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line
        body: Email body content
        sender: Sender email address
        
    Returns:
        Boolean indicating success (always True for mock)
    """
    print("=" * 60)
    print("📧 EMAIL SENT")
    print("=" * 60)
    print(f"From: {sender}")
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print("-" * 40)
    print(body)
    print("=" * 60)
    
    logger.info(f"Email sent to {recipient_email} with subject: {subject}")
    return True

def schedule_callback(phone_number: str, preferred_time: str, contact_name: str, notes: str = "") -> Dict[str, Any]:
    """
    Mock function to simulate scheduling a callback.
    
    Args:
        phone_number: Phone number for the callback
        preferred_time: Preferred time for callback
        contact_name: Name of the contact person
        notes: Additional notes about the callback
        
    Returns:
        Dictionary containing callback details
    """
    # Generate a mock callback ID and schedule
    callback_id = f"CB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    scheduled_time = datetime.now() + timedelta(hours=24)  # Default to 24 hours from now
    
    callback_details = {
        "callback_id": callback_id,
        "phone_number": phone_number,
        "contact_name": contact_name,
        "preferred_time": preferred_time,
        "scheduled_time": scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
        "notes": notes,
        "status": "scheduled"
    }
    
    print("=" * 60)
    print("📞 CALLBACK SCHEDULED")
    print("=" * 60)
    print(f"Callback ID: {callback_id}")
    print(f"Contact: {contact_name}")
    print(f"Phone: {phone_number}")
    print(f"Preferred Time: {preferred_time}")
    print(f"Scheduled For: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if notes:
        print(f"Notes: {notes}")
    print("=" * 60)
    
    logger.info(f"Callback scheduled for {contact_name} at {phone_number}")
    return callback_details

def log_lead_information(lead_data: Dict[str, Any]) -> bool:
    """
    Mock function to log new lead information to CRM system.
    
    Args:
        lead_data: Dictionary containing lead information
        
    Returns:
        Boolean indicating success
    """
    lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print("=" * 60)
    print("📝 NEW LEAD LOGGED")
    print("=" * 60)
    print(f"Lead ID: {lead_id}")
    for key, value in lead_data.items():
        if value:  # Only show non-empty values
            print(f"{key.replace('_', ' ').title()}: {value}")
    print("=" * 60)
    
    logger.info(f"New lead logged with ID: {lead_id}")
    return True

def create_follow_up_task(pharmacy_name: str, contact_info: Dict[str, str], task_type: str = "follow_up") -> Dict[str, Any]:
    """
    Mock function to create a follow-up task in the CRM system.
    
    Args:
        pharmacy_name: Name of the pharmacy
        contact_info: Dictionary containing contact information
        task_type: Type of follow-up task
        
    Returns:
        Dictionary containing task details
    """
    task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    due_date = datetime.now() + timedelta(days=3)  # Due in 3 days
    
    task_details = {
        "task_id": task_id,
        "pharmacy_name": pharmacy_name,
        "contact_info": contact_info,
        "task_type": task_type,
        "due_date": due_date.strftime("%Y-%m-%d"),
        "status": "pending",
        "priority": "medium"
    }
    
    print("=" * 60)
    print("✅ FOLLOW-UP TASK CREATED")
    print("=" * 60)
    print(f"Task ID: {task_id}")
    print(f"Pharmacy: {pharmacy_name}")
    print(f"Type: {task_type}")
    print(f"Due Date: {due_date.strftime('%Y-%m-%d')}")
    print(f"Contact Info: {contact_info}")
    print("=" * 60)
    
    logger.info(f"Follow-up task created for {pharmacy_name}")
    return task_details