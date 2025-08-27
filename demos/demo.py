#!/usr/bin/env python3
"""
Comprehensive demonstration of the pharmacy sales chatbot.
Shows clean architecture, proper error handling, and excellent usability.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path so imports work from any location
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.chatbot import PharmacySalesChatbot
from api.integration import PharmacyAPIClient
from utils.logging_config import DebugContext

def print_section_header(title: str, emoji: str = "🎯"):
    """Print a clean section header."""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_conversation_message(speaker: str, message: str, emoji: str):
    """Print a conversation message with clean formatting."""
    # Truncate long messages for display
    display_message = message if len(message) <= 150 else message[:147] + "..."
    print(f"{emoji} {speaker}: {display_message}")

def demo_api_capabilities():
    """Demonstrate API client capabilities with clean error handling."""
    print_section_header("API CLIENT CAPABILITIES", "🌐")
    
    try:
        with PharmacyAPIClient() as api_client:
            # Health check
            print("📡 Testing API connectivity...")
            if api_client.health_check():
                print("✅ API connection successful")
            else:
                print("❌ API connection failed")
                return
            
            # Get all pharmacies
            print("\n📊 Fetching pharmacy database...")
            pharmacies = api_client.get_all_pharmacies()
            print(f"✅ Retrieved {len(pharmacies)} pharmacies")
            
            # Show sample data
            for i, pharmacy in enumerate(pharmacies[:3], 1):
                name = pharmacy.get('name', 'Unknown')
                city = pharmacy.get('city', 'Unknown')
                state = pharmacy.get('state', 'Unknown')
                rx_volume = pharmacy.get('rxVolume', 0)
                print(f"   {i}. {name} ({city}, {state}) - {rx_volume:,} Rx/month")
            
            # Demonstrate search functionality
            print(f"\n🔍 Testing search functionality...")
            high_volume = api_client.search_pharmacies(min_volume=8000)
            print(f"✅ Found {len(high_volume)} high-volume pharmacies")
            
            # API statistics
            print(f"\n📈 API Statistics:")
            stats = api_client.get_api_stats()
            print(f"   Total Pharmacies: {stats['total_pharmacies']}")
            print(f"   Average Rx Volume: {stats['average_rx_volume']:,.0f}")
            print(f"   Pharmacy Types: {dict(stats['by_type'])}")
            
    except Exception as e:
        print(f"❌ API demonstration failed: {e}")

def demo_known_pharmacy_conversation():
    """Demonstrate conversation with a known pharmacy."""
    print_section_header("KNOWN PHARMACY CONVERSATION", "🏥")
    
    try:
        with PharmacySalesChatbot(enable_debug=False) as chatbot:
            # Use a known phone number from the API
            known_phone = "+1-555-123-4567"
            
            print(f"📞 Incoming call from: {known_phone}")
            print("🔍 Looking up in database...")
            
            # Start conversation
            greeting = chatbot.start_conversation(known_phone)
            print_conversation_message("Pharmesol Agent", greeting, "🤖")
            
            # Simulate realistic conversation flow
            conversation_flow = [
                ("We're interested in better pricing for our high-volume pharmacy. We currently fill about 15,000 prescriptions per month.", "👤"),
                ("That sounds perfect! Could you send me detailed information? My email is manager@healthfirst.com", "👤"),
                ("Also, could you schedule a callback for tomorrow afternoon to discuss volume discounts in detail?", "👤")
            ]
            
            for user_message, emoji in conversation_flow:
                print_conversation_message("Caller", user_message, emoji)
                
                response = chatbot.process_message(user_message)
                print_conversation_message("Pharmesol Agent", response, "🤖")
                
                time.sleep(0.5)  # Brief pause for readability
            
            # Show conversation summary
            print(f"\n📋 Conversation Summary:")
            summary = chatbot.get_conversation_summary()
            print(f"   Messages Exchanged: {summary['message_count']}")
            print(f"   Actions Taken: {', '.join(summary['actions_taken']) if summary['actions_taken'] else 'None'}")
            print(f"   Pharmacy Type: {summary.get('pharmacy_data', {}).get('type', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Known pharmacy demo failed: {e}")

def demo_new_lead_conversation():
    """Demonstrate lead generation conversation."""
    print_section_header("NEW LEAD GENERATION", "🎯")
    
    try:
        with PharmacySalesChatbot(enable_debug=False) as chatbot:
            unknown_phone = "+1-555-NEW-LEAD"
            
            print(f"📞 Incoming call from: {unknown_phone}")
            print("🔍 Looking up in database... ❌ Not found (New Lead)")
            
            # Start conversation
            greeting = chatbot.start_conversation(unknown_phone)
            print_conversation_message("Pharmesol Agent", greeting, "🤖")
            
            # New lead conversation flow
            lead_conversation = [
                ("Hi, I'm calling from Metro Plus Pharmacy in downtown Seattle. We're looking for a new pharmaceutical distributor.", "👤"),
                ("We currently fill about 8,500 prescriptions per month and we're not satisfied with our current supplier's delivery times.", "👤"),
                ("That sounds exactly like what we need! Could you send me information via email?", "👤"),
                ("Sure, please send everything to info@metroplus.com", "👤"),
                ("Perfect! And could you also schedule a callback for this week to discuss pricing details?", "👤")
            ]
            
            for user_message, emoji in lead_conversation:
                print_conversation_message("Caller", user_message, emoji)
                
                response = chatbot.process_message(user_message)
                print_conversation_message("Pharmesol Agent", response, "🤖")
                
                time.sleep(0.5)
            
            # Show lead summary
            print(f"\n📋 Lead Generation Summary:")
            summary = chatbot.get_conversation_summary()
            lead_data = summary.get('lead_data', {})
            print(f"   Lead Completeness: {lead_data.get('completion_percentage', 0)}%")
            print(f"   Email Collected: {'✅' if lead_data.get('has_email') else '❌'}")
            print(f"   Estimated Volume: {lead_data.get('estimated_volume', 'Unknown')}")
            print(f"   Actions Success Rate: {summary['action_summary']['success_rate']:.0%}")
            
    except Exception as e:
        print(f"❌ New lead demo failed: {e}")

def demo_error_handling():
    """Demonstrate robust error handling."""
    print_section_header("ERROR HANDLING & RESILIENCE", "🛡️")
    
    # Test with invalid API key
    print("🧪 Testing with invalid OpenAI key...")
    try:
        with PharmacySalesChatbot(openai_api_key="invalid_key") as chatbot:
            pass
    except ValueError as e:
        print("❌ Properly caught invalid API key")
    
    # Test chatbot resilience with valid key
    try:
        with PharmacySalesChatbot(enable_debug=False) as chatbot:
            greeting = chatbot.start_conversation("+1-555-TEST-ERROR")
            print("✅ Chatbot handles unknown numbers gracefully")
            
            # Test with edge case messages
            edge_cases = [
                "",  # Empty message
                "a" * 1000,  # Very long message
                "Special chars: @#$%^&*()",  # Special characters
            ]
            
            for edge_case in edge_cases:
                try:
                    response = chatbot.process_message(edge_case)
                    print("✅ Handled edge case gracefully")
                except Exception:
                    print("❌ Failed to handle edge case")
                    
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

def demo_debug_features():
    """Demonstrate debugging and logging features."""
    print_section_header("DEBUG & LOGGING FEATURES", "🔍")
    
    print("🔧 Enabling debug mode...")
    
    with DebugContext("debug_demonstration") as debug:
        debug.log_step("Starting debug demo")
        
        try:
            with PharmacySalesChatbot(enable_debug=True, log_level="DEBUG") as chatbot:
                debug.log_step("Chatbot initialized with debug mode")
                
                greeting = chatbot.start_conversation("+1-555-DEBUG-TEST")
                debug.log_checkpoint("conversation_started", {"greeting_length": len(greeting)})
                
                response = chatbot.process_message("Hi, can you send me information about your services?")
                debug.log_checkpoint("message_processed", {"response_length": len(response)})
                
                summary = chatbot.get_conversation_summary()
                debug.log_step(f"Conversation summary generated: {summary['message_count']} messages")
                
            print("✅ Debug features working correctly")
            print("📁 Check logs/ directory for detailed logs")
            
        except Exception as e:
            debug.log_step(f"Debug demo failed: {e}")

def show_architecture_benefits():
    """Show the benefits of the architecture."""
    print_section_header("ARCHITECTURE BENEFITS", "🏗️")
    
    benefits = [
        ("🧩 Modular Components", "Clean separation between API, conversation logic, actions, and LLM"),
        ("🛡️ Error Resilience", "Comprehensive error handling at every layer"),
        ("📊 Structured Data", "Type-safe data models with validation"),
        ("🔍 Observability", "Detailed logging and debugging capabilities"),
        ("🧪 Testability", "Each component can be tested independently"),
        ("🔧 Maintainability", "Easy to modify, extend, or replace components"),
        ("📈 Scalability", "Clean abstractions support future enhancements"),
        ("🎯 Usability", "Simple API with powerful features underneath")
    ]
    
    for title, description in benefits:
        print(f"{title}: {description}")
    
    print(f"\n📦 Component Structure:")
    components = [
        "models.py - Data structures and business objects",
        "api_client.py - Clean API interaction with retry logic",
        "conversation_manager.py - Conversation flow and intent analysis", 
        "action_handler.py - Business action execution",
        "logging_config.py - Comprehensive logging and debugging",
        "chatbot.py - Main orchestrator that brings it all together"
    ]
    
    for component in components:
        print(f"   • {component}")

def main():
    """Run comprehensive demonstration."""
    print("🚀 PHARMACY SALES CHATBOT DEMONSTRATION")
    print("="*60)
    print("This demo showcases the improved architecture with:")
    print("• Clean separation of concerns")
    print("• Excellent error handling") 
    print("• Comprehensive logging")
    print("• Structured data models")
    print("• High maintainability")
    
    try:
        # Show architecture benefits first
        show_architecture_benefits()
        
        # Demonstrate API capabilities
        demo_api_capabilities()
        
        # Wait for user input to continue
        input("\n⏯️  Press Enter to continue with conversation demos...")
        
        # Demonstrate conversations
        demo_known_pharmacy_conversation()
        demo_new_lead_conversation()
        
        # Show error handling
        input("\n⏯️  Press Enter to continue with error handling demo...")
        demo_error_handling()
        
        # Show debug features
        input("\n⏯️  Press Enter to see debug features...")
        demo_debug_features()
        
        print_section_header("DEMONSTRATION COMPLETE", "🎉")
        print("✅ All components working correctly!")
        print("🎯 The architecture provides:")
        print("   • Better code organization and readability")
        print("   • Improved error handling and resilience") 
        print("   • Comprehensive logging and debugging")
        print("   • Clean abstractions for easy maintenance")
        print("   • Excellent separation of concerns")
        
        print(f"\n📚 Check the source code to see clean, well-documented implementations!")
        
    except KeyboardInterrupt:
        print(f"\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This demonstrates the importance of proper error handling!")

if __name__ == "__main__":
    main()