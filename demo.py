#!/usr/bin/env python3
"""
Quick demonstration of the pharmacy sales chatbot without requiring OpenAI API key.
Shows core functionality including API lookup and mock functions.
"""

import sys
import time
from integration import PharmacyLookup
from function_calls import send_email, schedule_callback, log_lead_information

def print_divider(title=""):
    """Print a section divider."""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("="*60)

def simulate_typing(text, delay=0.03):
    """Simulate typing effect for demo purposes."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def demo_api_integration():
    """Demonstrate API integration functionality."""
    print_divider("API INTEGRATION DEMO")
    
    lookup = PharmacyLookup()
    
    print("📡 Fetching all pharmacies from API...")
    all_pharmacies = lookup.get_all_pharmacies()
    
    if all_pharmacies:
        print(f"✅ Successfully connected to API. Found {len(all_pharmacies)} pharmacies:")
        for i, pharmacy in enumerate(all_pharmacies, 1):
            name = pharmacy.get('name', 'Unknown')
            phone = pharmacy.get('phone', 'No phone')
            city = pharmacy.get('city', 'Unknown city')
            print(f"   {i}. {name} - {phone} - {city}")
        
        # Test lookup with first pharmacy
        if all_pharmacies:
            test_pharmacy = all_pharmacies[0]
            test_phone = test_pharmacy.get('phone')
            
            print(f"\n🔍 Testing lookup with phone: {test_phone}")
            result = lookup.lookup_pharmacy_by_phone(test_phone)
            if result:
                print(f"✅ Lookup successful! Found: {result.get('name', 'Unknown')}")
            else:
                print("❌ Lookup failed")
        
        # Test with unknown phone
        print(f"\n🔍 Testing lookup with unknown phone: +1-555-999-8888")
        result = lookup.lookup_pharmacy_by_phone("+1-555-999-8888")
        if result:
            print(f"Found: {result.get('name', 'Unknown')}")
        else:
            print("✅ Correctly returned None for unknown phone number")
            
    else:
        print("❌ Could not connect to API or no pharmacies found")

def demo_known_pharmacy_scenario():
    """Demonstrate handling a call from a known pharmacy."""
    print_divider("KNOWN PHARMACY CALL SIMULATION")
    
    # Get a real pharmacy from the API
    lookup = PharmacyLookup()
    all_pharmacies = lookup.get_all_pharmacies()
    
    if not all_pharmacies:
        print("⚠️  API not available, using mock data")
        pharmacy_data = {
            "name": "HealthFirst Pharmacy",
            "phone": "+1-555-123-4567",
            "city": "Springfield",
            "state": "IL",
            "rxVolume": 15000
        }
    else:
        pharmacy_data = all_pharmacies[0]
        # Add mock rxVolume if not present
        if 'rxVolume' not in pharmacy_data:
            pharmacy_data['rxVolume'] = 12000
    
    phone = pharmacy_data.get('phone', '+1-555-123-4567')
    name = pharmacy_data.get('name', 'Unknown Pharmacy')
    
    print(f"📞 INCOMING CALL FROM: {phone}")
    print(f"🔍 Looking up pharmacy in database...")
    
    print(f"✅ Found in database: {name}")
    if pharmacy_data.get('city') and pharmacy_data.get('state'):
        print(f"   Location: {pharmacy_data['city']}, {pharmacy_data['state']}")
    if pharmacy_data.get('rxVolume'):
        print(f"   Rx Volume: {pharmacy_data['rxVolume']:,}/month")
    
    print(f"\n💬 CONVERSATION START")
    print("-" * 40)
    
    # Simulate greeting
    location_str = ""
    if pharmacy_data.get('city') and pharmacy_data.get('state'):
        location_str = f" in {pharmacy_data['city']}, {pharmacy_data['state']}"
    
    rx_volume = pharmacy_data.get('rxVolume', 0)
    if rx_volume >= 10000:
        volume_msg = "With your high prescription volume, you'd be an excellent fit for our premium tier services."
    elif rx_volume >= 5000:
        volume_msg = "Your prescription volume puts you in a great position to benefit from our bulk pricing."
    else:
        volume_msg = "We can offer competitive pricing and room to grow with our flexible service options."
    
    greeting = f"Great! I see you're calling from {name}{location_str}. {volume_msg} How can Pharmesol help you today?"
    
    print("🤖 Pharmesol Agent:")
    simulate_typing(f"   {greeting}")
    
    # Simulate conversation
    print("\n👤 Caller:")
    simulate_typing("   We're interested in better pricing for high-volume pharmacies. Could you send me information at manager@healthfirst.com?")
    
    print("\n🤖 Pharmesol Agent:")
    simulate_typing("   Perfect! Let me send you detailed information about our high-volume pharmacy services right away.")
    
    # Demonstrate email sending
    print("\n📧 SENDING EMAIL...")
    send_email(
        recipient_email="manager@healthfirst.com",
        subject=f"Pharmesol Services Information for {name}",
        body=f"""Dear Manager,

Thank you for speaking with us today about Pharmesol's pharmacy distribution services.

Based on our conversation, here's what we can offer {name}:

• Competitive pricing on pharmaceutical products
• Reliable supply chain with consistent inventory
• Dedicated account management for high-volume pharmacies
• Flexible delivery schedules to meet your needs

I'll be following up with you within the next few business days.

Best regards,
Pharmesol Sales Team"""
    )

def demo_unknown_pharmacy_scenario():
    """Demonstrate handling a call from an unknown pharmacy (lead generation)."""
    print_divider("UNKNOWN PHARMACY CALL SIMULATION")
    
    unknown_phone = "+1-555-999-1234"
    
    print(f"📞 INCOMING CALL FROM: {unknown_phone}")
    print(f"🔍 Looking up pharmacy in database...")
    
    lookup = PharmacyLookup()
    result = lookup.lookup_pharmacy_by_phone(unknown_phone)
    
    if result:
        print(f"✅ Found: {result.get('name', 'Unknown')}")
    else:
        print("❌ Pharmacy not found in database - treating as new lead")
    
    print(f"\n💬 CONVERSATION START")
    print("-" * 40)
    
    print("🤖 Pharmesol Agent:")
    simulate_typing("   Thank you for calling Pharmesol! I don't have your information in our system yet.")
    simulate_typing("   Could you please tell me your pharmacy name, location, and monthly prescription volume?")
    
    print("\n👤 Caller:")
    simulate_typing("   Hi, I'm calling from MediCare Plus Pharmacy in downtown Chicago.")
    simulate_typing("   We fill about 8,000 prescriptions per month and we're looking for a new distributor.")
    
    print("\n🤖 Pharmesol Agent:")
    simulate_typing("   Thank you! MediCare Plus sounds like a great fit for our services.")
    simulate_typing("   With 8,000 prescriptions monthly, you'd benefit from our volume pricing and reliable delivery.")
    
    print("\n👤 Caller:")
    simulate_typing("   That sounds promising! Could you send me information at info@medicareplus.com")
    simulate_typing("   and also schedule a callback for tomorrow afternoon?")
    
    print("\n🤖 Pharmesol Agent:")
    simulate_typing("   Absolutely! Let me take care of both of those for you right now.")
    
    # Demonstrate lead logging
    print("\n📝 LOGGING NEW LEAD...")
    lead_data = {
        "pharmacy_name": "MediCare Plus Pharmacy",
        "location": "Chicago, IL",
        "rx_volume": 8000,
        "email": "info@medicareplus.com",
        "phone": unknown_phone,
        "interest": "New distributor - volume pricing"
    }
    log_lead_information(lead_data)
    
    # Demonstrate email sending
    print("\n📧 SENDING FOLLOW-UP EMAIL...")
    send_email(
        recipient_email="info@medicareplus.com",
        subject="Welcome to Pharmesol - MediCare Plus Pharmacy",
        body=f"""Dear MediCare Plus Team,

Thank you for your interest in Pharmesol's pharmacy distribution services.

Based on our conversation, here's what we can offer your pharmacy:

• Volume-based pricing for 8,000+ monthly prescriptions
• Reliable supply chain with flexible delivery schedules
• Dedicated customer support
• Growth-oriented service options

Our team will call you back tomorrow afternoon as requested to discuss specific pricing and service details.

Best regards,
Pharmesol Sales Team"""
    )
    
    # Demonstrate callback scheduling
    print("\n📞 SCHEDULING CALLBACK...")
    schedule_callback(
        phone_number=unknown_phone,
        preferred_time="tomorrow afternoon",
        contact_name="MediCare Plus Pharmacy",
        notes="New lead - 8K Rx/month, interested in volume pricing, requested callback"
    )

def demo_mock_functions():
    """Demonstrate all mock functions."""
    print_divider("MOCK FUNCTIONS DEMO")
    
    print("Testing all utility functions:\n")
    
    # Test email function
    print("1. 📧 Email Function:")
    send_email(
        recipient_email="demo@pharmacy.com",
        subject="Demo Email",
        body="This is a demonstration of the email functionality."
    )
    
    # Test callback scheduling
    print("\n2. 📞 Callback Scheduling:")
    schedule_callback(
        phone_number="+1-555-DEMO-123",
        preferred_time="next business day",
        contact_name="Demo Pharmacy",
        notes="Demonstration callback"
    )
    
    # Test lead logging
    print("\n3. 📝 Lead Logging:")
    demo_lead = {
        "pharmacy_name": "Demo Pharmacy",
        "contact_name": "John Smith",
        "email": "demo@pharmacy.com",
        "phone": "+1-555-DEMO-123",
        "location": "Demo City, ST",
        "rx_volume": 5000,
        "notes": "Interested in bulk pricing"
    }
    log_lead_information(demo_lead)

def main():
    """Main demo function."""
    print("🏥 PHARMESOL PHARMACY SALES CHATBOT")
    print("   Complete System Demonstration")
    print("="*60)
    print("This demonstration shows the core functionality without")
    print("requiring an OpenAI API key. Set OPENAI_API_KEY to")
    print("enable full conversational AI features.")
    
    try:
        # Run demonstrations
        demo_api_integration()
        input("\nPress Enter to continue to known pharmacy scenario...")
        
        demo_known_pharmacy_scenario()
        input("\nPress Enter to continue to unknown pharmacy scenario...")
        
        demo_unknown_pharmacy_scenario()
        input("\nPress Enter to see mock functions demo...")
        
        demo_mock_functions()
        
        print_divider("DEMONSTRATION COMPLETE")
        print("✅ All core functionality demonstrated successfully!")
        print("\n📋 Summary of capabilities:")
        print("   • API integration with external pharmacy database")
        print("   • Automatic phone number lookup and pharmacy identification")
        print("   • Personalized conversations based on pharmacy data")
        print("   • Lead generation for unknown callers")
        print("   • Email automation for follow-up")
        print("   • Callback scheduling system")
        print("   • CRM integration simulation")
        print("\n🚀 To enable full AI conversations, set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   python main.py interactive")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is likely due to network connectivity issues.")

if __name__ == "__main__":
    main()