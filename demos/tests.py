"""
Comprehensive test suite for the pharmacy sales chatbot.
Tests API integration, chatbot functionality, and edge cases.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import requests
from api.integration import PharmacyLookup
from api.llm import PharmacyChatbot
from utils.function_calls import send_email, schedule_callback, log_lead_information

class TestPharmacyLookup(unittest.TestCase):
    """Test cases for pharmacy API integration."""
    
    def setUp(self):
        self.lookup = PharmacyLookup()
    
    @patch('api.integration.requests.get')
    def test_lookup_existing_pharmacy(self, mock_get):
        """Test successful pharmacy lookup."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "name": "Central Pharmacy",
                "phone": "+1234567890",
                "city": "Springfield",
                "state": "IL",
                "rxVolume": 15000
            },
            {
                "id": "2", 
                "name": "Corner Drugstore",
                "phone": "+1987654321",
                "city": "Shelbyville",
                "state": "IL", 
                "rxVolume": 8000
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test lookup
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Central Pharmacy")
        self.assertEqual(result['rxVolume'], 15000)
        self.assertEqual(result['city'], "Springfield")
    
    @patch('api.integration.requests.get')
    def test_lookup_nonexistent_pharmacy(self, mock_get):
        """Test lookup for phone number not in database."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "name": "Central Pharmacy", 
                "phone": "+1234567890",
                "city": "Springfield",
                "state": "IL",
                "rxVolume": 15000
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test lookup with different phone number
        result = self.lookup.lookup_pharmacy_by_phone("+1555555555")
        
        self.assertIsNone(result)
    
    @patch('api.integration.requests.get')
    def test_api_request_failure(self, mock_get):
        """Test handling of API request failures."""
        # Mock request exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNone(result)
    
    @patch('api.integration.requests.get')
    def test_malformed_api_response(self, mock_get):
        """Test handling of malformed API responses."""
        # Mock malformed response
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNone(result)
    
    @patch('api.integration.requests.get')
    def test_missing_phone_field(self, mock_get):
        """Test handling of API response missing phone field."""
        # Mock API response with missing phone field
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "name": "Central Pharmacy",
                # "phone" field missing
                "city": "Springfield",
                "state": "IL",
                "rxVolume": 15000
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNone(result)
    
    @patch('api.integration.requests.get')
    def test_empty_api_response(self, mock_get):
        """Test handling of empty API response."""
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNone(result)

class TestPharmacyChatbot(unittest.TestCase):
    """Test cases for chatbot functionality."""
    
    def setUp(self):
        # Mock OpenAI API key for testing
        self.chatbot = PharmacyChatbot(openai_api_key="test_key")
        self.chatbot.client = Mock()
    
    def test_start_conversation_known_pharmacy(self):
        """Test conversation start with known pharmacy."""
        pharmacy_data = {
            "name": "Central Pharmacy",
            "city": "Springfield", 
            "state": "IL",
            "rxVolume": 15000
        }
        
        greeting = self.chatbot.start_conversation("+1234567890", pharmacy_data)
        
        self.assertIn("Central Pharmacy", greeting)
        self.assertIn("Springfield", greeting)
        self.assertIn("high prescription volume", greeting)
    
    def test_start_conversation_unknown_pharmacy(self):
        """Test conversation start with unknown pharmacy."""
        greeting = self.chatbot.start_conversation("+1555555555", None)
        
        self.assertIn("Thank you for calling Pharmesol", greeting)
        self.assertIn("pharmacy name", greeting)
        self.assertIn("location", greeting)
        self.assertIn("prescriptions", greeting)
    
    def test_email_request_handling(self):
        """Test handling of email requests."""
        self.chatbot.start_conversation("+1234567890", None)
        
        # Mock send_email function
        with patch('api.llm.send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = self.chatbot.process_user_message("Please send me information at test@pharmacy.com")
            
            mock_send_email.assert_called_once()
            self.assertIn("sent detailed information", response)
            self.assertIn("test@pharmacy.com", response)
    
    def test_callback_request_handling(self):
        """Test handling of callback requests."""
        self.chatbot.start_conversation("+1234567890", None)
        
        # Mock callback functions
        with patch('api.llm.schedule_callback') as mock_schedule, \
             patch('api.llm.create_follow_up_task') as mock_follow_up:
            
            mock_schedule.return_value = {"callback_id": "CB-123", "status": "scheduled"}
            mock_follow_up.return_value = {"task_id": "TASK-123"}
            
            response = self.chatbot.process_user_message("Please call me back tomorrow morning")
            
            mock_schedule.assert_called_once()
            mock_follow_up.assert_called_once()
            self.assertIn("scheduled a callback", response)
    
    def test_lead_information_extraction(self):
        """Test extraction of lead information from messages."""
        self.chatbot.start_conversation("+1555555555", None)
        
        message = "Hi, I'm calling from Springfield Pharmacy in Springfield, IL. My email is manager@springfieldpharm.com"
        self.chatbot._extract_lead_information(message)
        
        self.assertEqual(self.chatbot.lead_data['email'], 'manager@springfieldpharm.com')
        self.assertIn('pharmacy_name', self.chatbot.lead_data)
    
    @patch('api.llm.OpenAI')
    def test_llm_api_failure_handling(self, mock_openai):
        """Test handling of LLM API failures."""
        # Mock LLM API failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        chatbot = PharmacyChatbot(openai_api_key="test_key")
        chatbot.start_conversation("+1234567890", None)
        
        response = chatbot.process_user_message("Hello")
        
        self.assertIn("technical difficulties", response)
    
    def test_conversation_summary(self):
        """Test conversation summary generation."""
        pharmacy_data = {"name": "Test Pharmacy", "rxVolume": 10000}
        self.chatbot.start_conversation("+1234567890", pharmacy_data)
        self.chatbot.lead_data = {"email": "test@test.com"}
        
        summary = self.chatbot.get_conversation_summary()
        
        self.assertEqual(summary['phone_number'], "+1234567890")
        self.assertEqual(summary['pharmacy_data'], pharmacy_data)
        self.assertEqual(summary['lead_data'], {"email": "test@test.com"})
        self.assertGreater(summary['conversation_length'], 0)

class TestMockFunctions(unittest.TestCase):
    """Test cases for mock utility functions."""
    
    def test_send_email_function(self):
        """Test send_email mock function."""
        result = send_email(
            recipient_email="test@pharmacy.com",
            subject="Test Subject",
            body="Test body content"
        )
        
        self.assertTrue(result)
    
    def test_schedule_callback_function(self):
        """Test schedule_callback mock function."""
        result = schedule_callback(
            phone_number="+1234567890",
            preferred_time="tomorrow morning", 
            contact_name="John Doe",
            notes="Test callback"
        )
        
        self.assertIn('callback_id', result)
        self.assertIn('phone_number', result)
        self.assertIn('contact_name', result)
        self.assertEqual(result['status'], 'scheduled')
    
    def test_log_lead_information_function(self):
        """Test log_lead_information mock function."""
        lead_data = {
            "pharmacy_name": "Test Pharmacy",
            "email": "test@test.com",
            "phone": "+1234567890"
        }
        
        result = log_lead_information(lead_data)
        
        self.assertTrue(result)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        self.chatbot = PharmacyChatbot(openai_api_key="test_key")
        self.chatbot.client = Mock()
        self.lookup = PharmacyLookup()
    
    def test_missing_openai_key(self):
        """Test chatbot initialization without OpenAI key."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                PharmacyChatbot()
    
    @patch('api.integration.requests.get')
    def test_api_timeout(self, mock_get):
        """Test API timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNone(result)
    
    def test_invalid_phone_number_format(self):
        """Test handling of invalid phone number formats."""
        self.chatbot.start_conversation("invalid_phone", None)
        
        # Should still work, just with the invalid format stored
        self.assertEqual(self.chatbot.phone_number, "invalid_phone")
    
    @patch('api.integration.requests.get')
    def test_partial_pharmacy_data(self, mock_get):
        """Test handling of pharmacy data with missing fields."""
        # Mock API response with partial data
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "name": "Partial Pharmacy",
                "phone": "+1234567890",
                # Missing city, state, rxVolume
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.lookup.lookup_pharmacy_by_phone("+1234567890")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Partial Pharmacy")
        # Missing fields should be handled gracefully
    
    def test_empty_user_message(self):
        """Test handling of empty user messages."""
        self.chatbot.start_conversation("+1234567890", None)
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I didn't catch that. Could you please repeat?"
        self.chatbot.client.chat.completions.create.return_value = mock_response
        
        response = self.chatbot.process_user_message("")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

def run_integration_tests():
    """Run integration tests with real API (if available)."""
    print("\n" + "="*60)
    print("INTEGRATION TESTS")
    print("="*60)
    
    try:
        # Test real API lookup
        lookup = PharmacyLookup()
        print("Testing real API connection...")
        
        # Try to get all pharmacies first
        all_pharmacies = lookup.get_all_pharmacies()
        if all_pharmacies:
            print(f"✅ API connection successful. Found {len(all_pharmacies)} pharmacies.")
            
            # Test lookup with first pharmacy's phone number
            if len(all_pharmacies) > 0:
                test_phone = all_pharmacies[0].get('phone')
                if test_phone:
                    result = lookup.lookup_pharmacy_by_phone(test_phone)
                    if result:
                        print(f"✅ Phone lookup successful for {result.get('name', 'Unknown')}")
                    else:
                        print("❌ Phone lookup failed")
                else:
                    print("⚠️ No phone number found in first pharmacy record")
        else:
            print("❌ API connection failed or returned empty results")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == '__main__':
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    run_integration_tests()