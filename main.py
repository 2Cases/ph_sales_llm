"""
Main chatbot simulation script for pharmacy sales inbound calls.
Demonstrates the functionality with sample scenarios.
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from api.integration import PharmacyLookup
from api.llm import PharmacyChatbot

# Load environment variables from .env file
load_dotenv()

def simulate_call(phone_number: str, openai_api_key: Optional[str] = None, interactive: bool = False):
    """
    Simulate an inbound call from a pharmacy.
    
    Args:
        phone_number: The caller's phone number
        openai_api_key: OpenAI API key (optional, will use environment variable if not provided)
        interactive: Whether to run in interactive mode
    """
    print("="*80)
    print(f"📞 INCOMING CALL FROM: {phone_number}")
    print("="*80)
    
    # Initialize components
    lookup = PharmacyLookup()
    
    try:
        chatbot = PharmacyChatbot(openai_api_key)
    except ValueError as e:
        print(f"❌ Error initializing chatbot: {e}")
        return
    
    # Step 1: Look up pharmacy in database
    print("🔍 Looking up pharmacy in database...")
    pharmacy_data = lookup.lookup_pharmacy_by_phone(phone_number)
    
    if pharmacy_data:
        print(f"✅ Found pharmacy: {pharmacy_data.get('name', 'Unknown')}")
        print(f"   Location: {pharmacy_data.get('city', 'Unknown')}, {pharmacy_data.get('state', 'Unknown')}")
        print(f"   Rx Volume: {pharmacy_data.get('rxVolume', 'Unknown')}/month")
    else:
        print("❌ Pharmacy not found in database - treating as new lead")
    
    # Step 2: Start conversation
    print("\n" + "="*80)
    print("💬 CONVERSATION START")
    print("="*80)
    
    greeting = chatbot.start_conversation(phone_number, pharmacy_data)
    print(f"🤖 Pharmesol Agent: {greeting}")
    
    if interactive:
        # Interactive mode - user can type responses
        print("\n[Interactive Mode - Type 'quit' to end conversation]")
        
        while True:
            user_input = input("\n👤 Caller: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                break
            
            if user_input:
                response = chatbot.process_user_message(user_input)
                print(f"🤖 Pharmesol Agent: {response}")
    else:
        # Automated demo scenarios
        if pharmacy_data:
            # Known pharmacy scenario
            demo_known_pharmacy_call(chatbot)
        else:
            # New lead scenario
            demo_new_lead_call(chatbot)
    
    # End conversation
    closing = chatbot.end_conversation()
    print(f"\n🤖 Pharmesol Agent: {closing}")
    
    # Show conversation summary
    print("\n" + "="*80)
    print("📋 CALL SUMMARY")
    print("="*80)
    summary = chatbot.get_conversation_summary()
    print(f"Phone Number: {summary['phone_number']}")
    print(f"Pharmacy Data: {'Found' if summary['pharmacy_data'] else 'Not Found'}")
    print(f"Lead Data Collected: {bool(summary['lead_data'])}")
    print(f"Conversation Length: {summary['conversation_length']} messages")
    print(f"Actions Taken: {', '.join(summary['actions_taken']) if summary['actions_taken'] else 'None'}")
    print("="*80)

def demo_known_pharmacy_call(chatbot: PharmacyChatbot):
    """Demonstrate a call from a known pharmacy."""
    print("\n[Simulating known pharmacy conversation...]")
    
    # Simulate customer responses
    responses = [
        "Hi, we're interested in learning more about your pricing for high-volume pharmacies.",
        "We currently fill about 15,000 prescriptions per month and are looking for better supplier terms.",
        "That sounds great. Could you send me some detailed information? My email is manager@centralpharmacy.com",
        "Yes, and also please schedule a callback for tomorrow morning to discuss this further."
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"\n👤 Caller: {response}")
        bot_response = chatbot.process_user_message(response)
        print(f"🤖 Pharmesol Agent: {bot_response}")

def demo_new_lead_call(chatbot: PharmacyChatbot):
    """Demonstrate a call from a new pharmacy (lead generation)."""
    print("\n[Simulating new lead conversation...]")
    
    # Simulate new lead responses
    responses = [
        "Hi, I'm calling from MedCare Pharmacy in downtown Chicago.",
        "We fill about 8,000 prescriptions per month and we're looking for a new pharmaceutical distributor.",
        "Our current supplier has been having delivery issues and their pricing isn't competitive anymore.",
        "That sounds promising. Could you send me information at info@medcarepharmacy.com?",
        "Yes, and please schedule a callback for this afternoon to discuss pricing details."
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"\n👤 Caller: {response}")
        bot_response = chatbot.process_user_message(response)
        print(f"🤖 Pharmesol Agent: {bot_response}")

def run_sample_scenarios():
    """Run predefined sample scenarios to demonstrate functionality."""
    print("🎭 RUNNING SAMPLE SCENARIOS")
    print("="*80)
    
    # Get OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️ OPENAI_API_KEY not set. LLM responses will be disabled.")
        print("   Set your OpenAI API key to see full functionality:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print()
    
    # First, let's check what pharmacies are available in the API
    print("🔍 Checking available pharmacies in API...")
    lookup = PharmacyLookup()
    all_pharmacies = lookup.get_all_pharmacies()
    
    if all_pharmacies:
        print(f"✅ Found {len(all_pharmacies)} pharmacies in database")
        for i, pharmacy in enumerate(all_pharmacies[:3], 1):  # Show first 3
            print(f"   {i}. {pharmacy.get('name', 'Unknown')} - {pharmacy.get('phone', 'No phone')}")
        if len(all_pharmacies) > 3:
            print(f"   ... and {len(all_pharmacies) - 3} more")
    else:
        print("❌ No pharmacies found or API connection failed")
    
    # Scenario 1: Known Pharmacy Call
    print(f"\n{'='*80}")
    print("📋 SCENARIO 1: KNOWN PHARMACY CALL")
    print("="*80)
    
    if all_pharmacies and len(all_pharmacies) > 0:
        test_pharmacy = all_pharmacies[0]
        test_phone = test_pharmacy.get('phone')
        if test_phone:
            simulate_call(test_phone, openai_key)
        else:
            print("⚠️ First pharmacy doesn't have a phone number, using mock number")
            simulate_call("+1234567890", openai_key)
    else:
        print("⚠️ Using mock data since API is unavailable")
        simulate_call("+1234567890", openai_key)
    
    # Scenario 2: Unknown Pharmacy Call (New Lead)
    print(f"\n{'='*80}")
    print("📋 SCENARIO 2: UNKNOWN PHARMACY CALL (NEW LEAD)")
    print("="*80)
    simulate_call("+1555123456", openai_key)  # Phone number not in database

def interactive_mode():
    """Run chatbot in interactive mode."""
    print("🎮 INTERACTIVE MODE")
    print("="*80)
    
    # Get OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not set. Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        return
    
    print("Enter a phone number to simulate an incoming call:")
    phone_number = input("📞 Phone Number: ").strip()
    
    if not phone_number:
        phone_number = "+1555000123"  # Default test number
        print(f"Using default number: {phone_number}")
    
    simulate_call(phone_number, openai_key, interactive=True)

def main():
    """Main entry point for the chatbot simulation."""
    print("🏥 PHARMESOL PHARMACY SALES CHATBOT SIMULATION")
    print("="*80)
    print("This simulation demonstrates an inbound call handling system")
    print("for pharmaceutical sales representatives.")
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'interactive':
            interactive_mode()
        elif command == 'test':
            # Run tests
            print("🧪 Running tests...")
            from tests import tests
            tests.run_all_tests()
            return
        elif command.startswith('+') or command.isdigit():
            # Phone number provided
            openai_key = os.getenv('OPENAI_API_KEY')
            simulate_call(command, openai_key, interactive=True)
        else:
            print("Usage:")
            print("  python main.py                 # Run sample scenarios")  
            print("  python main.py interactive     # Interactive mode")
            print("  python main.py test           # Run tests")
            print("  python main.py +1234567890    # Simulate call from specific number")
            return
    else:
        # Default: run sample scenarios
        run_sample_scenarios()

if __name__ == "__main__":
    main()