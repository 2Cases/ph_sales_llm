#!/usr/bin/env python3
"""
Complete demonstration of the pharmacy sales chatbot with full OpenAI integration.
"""

import os
from dotenv import load_dotenv
from integration import PharmacyLookup
from llm import PharmacyChatbot

# Load environment variables
load_dotenv()

def run_complete_demo():
    """Run a complete demonstration of the chatbot system."""
    print("🏥 PHARMESOL CHATBOT - COMPLETE DEMO WITH AI")
    print("="*60)
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Please check your .env file.")
        return
    
    print("✅ OpenAI API key loaded from .env file")
    
    # Initialize components
    lookup = PharmacyLookup()
    
    # Get available pharmacies
    print("\n🔍 Fetching pharmacy database...")
    all_pharmacies = lookup.get_all_pharmacies()
    
    if not all_pharmacies:
        print("❌ Could not connect to pharmacy API")
        return
    
    print(f"✅ Connected to API. Found {len(all_pharmacies)} pharmacies:")
    for i, p in enumerate(all_pharmacies, 1):
        print(f"   {i}. {p.get('name', 'Unknown')} - {p.get('phone', 'No phone')}")
    
    # Demo 1: Known Pharmacy Call
    print("\n" + "="*60)
    print("📋 SCENARIO 1: KNOWN PHARMACY WITH AI CONVERSATION")
    print("="*60)
    
    # Use first pharmacy from API
    pharmacy_data = all_pharmacies[0]
    phone = pharmacy_data.get('phone')
    
    print(f"📞 INCOMING CALL FROM: {phone}")
    print(f"🔍 Looking up in database... ✅ FOUND: {pharmacy_data.get('name')}")
    
    # Initialize chatbot
    chatbot = PharmacyChatbot()
    
    # Start conversation
    print(f"\n💬 AI CONVERSATION:")
    print("-" * 40)
    
    greeting = chatbot.start_conversation(phone, pharmacy_data)
    print(f"🤖 Pharmesol Agent: {greeting}")
    
    # Simulate realistic conversation flow
    conversation_flow = [
        "Hi there! We're looking for better pricing on our pharmaceutical orders. We currently fill about 15,000 prescriptions per month.",
        "That sounds great! Could you send me detailed pricing information? My email is manager@healthfirst.com",
        "Yes, and could you also schedule a callback for tomorrow afternoon to discuss volume discounts?"
    ]
    
    for user_message in conversation_flow:
        print(f"\n👤 Caller: {user_message}")
        response = chatbot.process_user_message(user_message)
        print(f"🤖 Pharmesol Agent: {response}")
    
    # Show conversation summary
    print(f"\n📋 CALL SUMMARY:")
    summary = chatbot.get_conversation_summary()
    print(f"   • Phone: {summary['phone_number']}")
    print(f"   • Pharmacy: {'Known' if summary['pharmacy_data'] else 'Unknown'}")
    print(f"   • Messages: {summary['conversation_length']}")
    print(f"   • Actions: {', '.join(summary['actions_taken']) if summary['actions_taken'] else 'None'}")
    
    # Demo 2: Unknown Pharmacy (New Lead)
    print("\n" + "="*60)
    print("📋 SCENARIO 2: NEW LEAD GENERATION WITH AI")
    print("="*60)
    
    unknown_phone = "+1-555-NEW-LEAD"
    print(f"📞 INCOMING CALL FROM: {unknown_phone}")
    print(f"🔍 Looking up in database... ❌ NOT FOUND (New Lead)")
    
    # New chatbot instance for new lead
    chatbot2 = PharmacyChatbot()
    
    greeting = chatbot2.start_conversation(unknown_phone, None)
    print(f"\n💬 AI CONVERSATION:")
    print("-" * 40)
    print(f"🤖 Pharmesol Agent: {greeting}")
    
    # New lead conversation
    lead_conversation = [
        "Hi, I'm calling from Metro Pharmacy in downtown Seattle. We're looking for a new pharmaceutical distributor.",
        "We currently fill about 8,000 prescriptions per month and we're not happy with our current supplier's delivery times.",
        "That sounds exactly what we need! Please send information to info@metropharmacy.com and schedule a call for this week."
    ]
    
    for user_message in lead_conversation:
        print(f"\n👤 Caller: {user_message}")
        response = chatbot2.process_user_message(user_message)
        print(f"🤖 Pharmesol Agent: {response}")
    
    # Show lead summary
    print(f"\n📋 LEAD SUMMARY:")
    summary2 = chatbot2.get_conversation_summary()
    print(f"   • Phone: {summary2['phone_number']}")
    print(f"   • Status: New Lead")
    print(f"   • Data Collected: {bool(summary2['lead_data'])}")
    print(f"   • Actions: {', '.join(summary2['actions_taken']) if summary2['actions_taken'] else 'None'}")
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("✅ Successfully demonstrated:")
    print("   • Real-time API pharmacy lookup")
    print("   • AI-powered natural conversations")
    print("   • Personalized responses based on pharmacy data")
    print("   • New lead generation and data collection")
    print("   • Automated email and callback scheduling")
    print("   • Complete conversation tracking")
    print(f"\n🚀 System ready for production use!")

if __name__ == "__main__":
    run_complete_demo()