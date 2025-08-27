"""
API integration module for pharmacy lookup and data retrieval.
Handles communication with the mockapi.io pharmacy database.
"""

import os
import requests
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PharmacyLookup:
    """Handles pharmacy data lookup from the external API."""
    
    def __init__(self, api_base_url: Optional[str] = None):
        # Use environment variable or provided URL or default
        self.api_base_url = (
            api_base_url or 
            os.getenv('PHARMACY_API_URL') or 
            "https://67e14fb758cc6bf785254550.mockapi.io"
        )
        self.pharmacies_endpoint = f"{self.api_base_url}/pharmacies"
    
    def lookup_pharmacy_by_phone(self, phone_number: str) -> Optional[Dict[Any, Any]]:
        """
        Look up pharmacy by phone number.
        
        Args:
            phone_number: The phone number to search for
            
        Returns:
            Dictionary containing pharmacy data if found, None otherwise
        """
        try:
            logger.info(f"Looking up pharmacy with phone number: {phone_number}")
            
            # Make API request
            response = requests.get(self.pharmacies_endpoint, timeout=10)
            response.raise_for_status()
            
            pharmacies = response.json()
            
            # Search for pharmacy by phone number
            for pharmacy in pharmacies:
                if pharmacy.get('phone') == phone_number:
                    logger.info(f"Found pharmacy: {pharmacy.get('name', 'Unknown')}")
                    return pharmacy
            
            logger.info(f"No pharmacy found for phone number: {phone_number}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during pharmacy lookup: {e}")
            return None
    
    def get_all_pharmacies(self) -> Optional[list]:
        """
        Retrieve all pharmacies from the API.
        
        Returns:
            List of all pharmacies or None if request fails
        """
        try:
            response = requests.get(self.pharmacies_endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve all pharmacies: {e}")
            return None