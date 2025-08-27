"""
API integration module for pharmacy lookup and data retrieval.
Handles communication with the mockapi.io pharmacy database with robust error handling and performance features.
"""

import os
import requests
import logging
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass

class PharmacyLookup:
    """
    Handles pharmacy data lookup from the external API with comprehensive error handling.
    
    Features:
    - Automatic retry logic for transient failures
    - Proper error handling and logging
    - Clean data transformation
    - Connection pooling for performance
    - Health checks and monitoring
    """
    
    def __init__(self, api_base_url: Optional[str] = None, timeout: int = 10, max_retries: int = 3):
        # Use environment variable or provided URL or default
        self.api_base_url = (
            api_base_url or 
            os.getenv('PHARMACY_API_URL') or 
            "https://67e14fb758cc6bf785254550.mockapi.io"
        ).rstrip('/')
        self.pharmacies_endpoint = f"{self.api_base_url}/pharmacies"
        self.timeout = timeout
        
        # Create session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy for resilience
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"Initialized API client for {self.api_base_url}")
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(
                self.pharmacies_endpoint,
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
            return False
    
    def lookup_pharmacy_by_phone(self, phone_number: str) -> Optional[Dict[Any, Any]]:
        """
        Look up pharmacy by phone number with improved error handling.
        
        Args:
            phone_number: The phone number to search for
            
        Returns:
            Dictionary containing pharmacy data if found, None otherwise
        """
        if not phone_number:
            logger.warning("Empty phone number provided for lookup")
            return None
        
        try:
            logger.info(f"Looking up pharmacy with phone number: {phone_number}")
            
            # Make API request with retry logic
            response = self.session.get(self.pharmacies_endpoint, timeout=self.timeout)
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
    
    def get_all_pharmacies(self) -> Optional[List[Dict[Any, Any]]]:
        """
        Retrieve all pharmacies from the API with robust error handling.
        
        Returns:
            List of all pharmacies or None if request fails
        """
        try:
            logger.debug("Fetching all pharmacies from API")
            
            response = self.session.get(self.pharmacies_endpoint, timeout=self.timeout)
            response.raise_for_status()
            
            raw_data = response.json()
            pharmacies = []
            
            # Validate and clean data
            for item in raw_data:
                if isinstance(item, dict):
                    pharmacies.append(item)
                else:
                    logger.warning(f"Skipping invalid pharmacy data: {item}")
            
            logger.info(f"Successfully retrieved {len(pharmacies)} pharmacies")
            return pharmacies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve pharmacies: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving pharmacies: {e}")
            return None
    
    def find_pharmacy_by_phone(self, phone_number: str) -> Optional[Dict[Any, Any]]:
        """
        Enhanced pharmacy lookup by phone number (alias for lookup_pharmacy_by_phone).
        
        Args:
            phone_number: The phone number to search for
            
        Returns:
            Dictionary containing pharmacy data if found, None otherwise
        """
        return self.lookup_pharmacy_by_phone(phone_number)
    
    def search_pharmacies(self, **filters) -> List[Dict[Any, Any]]:
        """
        Search pharmacies by various criteria.
        
        Args:
            **filters: Filtering criteria (e.g., city="Chicago", min_volume=5000)
            
        Returns:
            List of matching pharmacy dictionaries
        """
        try:
            all_pharmacies = self.get_all_pharmacies()
            if not all_pharmacies:
                return []
            
            results = []
            
            for pharmacy in all_pharmacies:
                matches = True
                
                # Apply filters
                if 'city' in filters and pharmacy.get('city'):
                    if pharmacy['city'].lower() != filters['city'].lower():
                        matches = False
                
                if 'state' in filters and pharmacy.get('state'):
                    if pharmacy['state'].lower() != filters['state'].lower():
                        matches = False
                
                if 'min_volume' in filters and pharmacy.get('rxVolume'):
                    if pharmacy['rxVolume'] < filters['min_volume']:
                        matches = False
                
                if 'max_volume' in filters and pharmacy.get('rxVolume'):
                    if pharmacy['rxVolume'] > filters['max_volume']:
                        matches = False
                
                if 'name' in filters and pharmacy.get('name'):
                    if filters['name'].lower() not in pharmacy['name'].lower():
                        matches = False
                
                if matches:
                    results.append(pharmacy)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_api_stats(self) -> dict:
        """
        Get statistics about the API data.
        
        Returns:
            Dictionary with API statistics
        """
        try:
            pharmacies = self.get_all_pharmacies()
            if not pharmacies:
                return {
                    'total_pharmacies': 0,
                    'by_type': {},
                    'by_state': {},
                    'total_rx_volume': 0,
                    'average_rx_volume': 0
                }
            
            total_count = len(pharmacies)
            by_type = {}
            by_state = {}
            total_volume = 0
            
            for pharmacy in pharmacies:
                # Count by volume type (categorize based on rx volume)
                rx_volume = pharmacy.get('rxVolume', 0)
                if rx_volume >= 10000:
                    pharmacy_type = 'high_volume'
                elif rx_volume >= 5000:
                    pharmacy_type = 'medium_volume'
                elif rx_volume >= 1000:
                    pharmacy_type = 'low_volume'
                else:
                    pharmacy_type = 'startup'
                
                by_type[pharmacy_type] = by_type.get(pharmacy_type, 0) + 1
                
                # Count by state
                state = pharmacy.get('state', 'Unknown')
                by_state[state] = by_state.get(state, 0) + 1
                
                # Sum volume
                if rx_volume:
                    total_volume += rx_volume
            
            return {
                'total_pharmacies': total_count,
                'by_type': by_type,
                'by_state': by_state,
                'total_rx_volume': total_volume,
                'average_rx_volume': total_volume / total_count if total_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get API stats: {e}")
            return {
                'total_pharmacies': 0,
                'by_type': {},
                'by_state': {},
                'total_rx_volume': 0,
                'average_rx_volume': 0
            }
    
    def get_high_volume_pharmacies(self, min_volume: int = 10000) -> List[Dict[Any, Any]]:
        """
        Get pharmacies with high prescription volume.
        
        Args:
            min_volume: Minimum volume threshold (default: 10,000)
            
        Returns:
            List of high-volume pharmacies
        """
        return self.search_pharmacies(min_volume=min_volume)
    
    def get_pharmacies_by_location(self, city: str = None, state: str = None) -> List[Dict[Any, Any]]:
        """
        Get pharmacies by location.
        
        Args:
            city: Filter by city (optional)
            state: Filter by state (optional)
            
        Returns:
            List of pharmacies matching location criteria
        """
        filters = {}
        if city:
            filters['city'] = city
        if state:
            filters['state'] = state
        
        return self.search_pharmacies(**filters)
    
    def close(self):
        """Clean up the session."""
        if hasattr(self, 'session'):
            self.session.close()
            logger.debug("API client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False  # Don't suppress exceptions

# Legacy alias for backward compatibility
PharmacyAPIClient = PharmacyLookup