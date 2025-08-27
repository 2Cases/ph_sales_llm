"""
Clean API client for pharmacy lookup with proper error handling and abstractions.
Focuses on reliability, readability, and maintainability.
"""

import os
import requests
import logging
from typing import Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from models import PharmacyData

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass

class PharmacyAPIClient:
    """
    Clean, well-structured API client for pharmacy data operations.
    
    Features:
    - Automatic retry logic for transient failures
    - Proper error handling and logging
    - Clean data transformation to structured models
    - Connection pooling for performance
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        # Use environment variable or provided URL or default
        self.base_url = (
            base_url or 
            os.getenv('PHARMACY_API_URL') or 
            "https://67e14fb758cc6bf785254550.mockapi.io"
        ).rstrip('/')
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
        
        logger.info(f"Initialized API client for {base_url}")
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/pharmacies",
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
            return False
    
    def get_all_pharmacies(self) -> List[PharmacyData]:
        """
        Retrieve all pharmacies with proper error handling.
        
        Returns:
            List of PharmacyData objects
            
        Raises:
            APIError: If the API request fails
        """
        try:
            logger.debug("Fetching all pharmacies from API")
            
            response = self.session.get(
                f"{self.base_url}/pharmacies",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            raw_data = response.json()
            pharmacies = []
            
            for item in raw_data:
                try:
                    pharmacy = PharmacyData.from_api_response(item)
                    pharmacies.append(pharmacy)
                except Exception as e:
                    logger.warning(f"Skipping invalid pharmacy data: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(pharmacies)} pharmacies")
            return pharmacies
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to retrieve pharmacies: {e}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error retrieving pharmacies: {e}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
    def find_pharmacy_by_phone(self, phone_number: str) -> Optional[PharmacyData]:
        """
        Find a specific pharmacy by phone number.
        
        Args:
            phone_number: The phone number to search for
            
        Returns:
            PharmacyData if found, None otherwise
            
        Raises:
            APIError: If the API request fails
        """
        if not phone_number:
            logger.warning("Empty phone number provided for lookup")
            return None
        
        try:
            logger.debug(f"Looking up pharmacy by phone: {phone_number}")
            
            # Get all pharmacies and search locally for better performance
            # In a real system, this might be a direct API call with query parameters
            all_pharmacies = self.get_all_pharmacies()
            
            for pharmacy in all_pharmacies:
                if pharmacy.phone == phone_number:
                    logger.info(f"Found pharmacy: {pharmacy.name}")
                    return pharmacy
            
            logger.debug(f"No pharmacy found for phone: {phone_number}")
            return None
            
        except APIError:
            # Re-raise API errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error during phone lookup: {e}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
    def search_pharmacies(self, **filters) -> List[PharmacyData]:
        """
        Search pharmacies by various criteria.
        
        Args:
            **filters: Filtering criteria (e.g., city="Chicago", min_volume=5000)
            
        Returns:
            List of matching PharmacyData objects
        """
        try:
            all_pharmacies = self.get_all_pharmacies()
            results = []
            
            for pharmacy in all_pharmacies:
                matches = True
                
                # Apply filters
                if 'city' in filters and pharmacy.city:
                    if pharmacy.city.lower() != filters['city'].lower():
                        matches = False
                
                if 'state' in filters and pharmacy.state:
                    if pharmacy.state.lower() != filters['state'].lower():
                        matches = False
                
                if 'min_volume' in filters and pharmacy.rx_volume:
                    if pharmacy.rx_volume < filters['min_volume']:
                        matches = False
                
                if 'max_volume' in filters and pharmacy.rx_volume:
                    if pharmacy.rx_volume > filters['max_volume']:
                        matches = False
                
                if matches:
                    results.append(pharmacy)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except APIError:
            raise
        except Exception as e:
            error_msg = f"Search failed: {e}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
    def get_api_stats(self) -> dict:
        """
        Get statistics about the API data.
        
        Returns:
            Dictionary with API statistics
        """
        try:
            pharmacies = self.get_all_pharmacies()
            
            total_count = len(pharmacies)
            by_type = {}
            by_state = {}
            total_volume = 0
            
            for pharmacy in pharmacies:
                # Count by type
                pharmacy_type = pharmacy.pharmacy_type.value
                by_type[pharmacy_type] = by_type.get(pharmacy_type, 0) + 1
                
                # Count by state
                state = pharmacy.state or 'Unknown'
                by_state[state] = by_state.get(state, 0) + 1
                
                # Sum volume
                if pharmacy.rx_volume:
                    total_volume += pharmacy.rx_volume
            
            return {
                'total_pharmacies': total_count,
                'by_type': by_type,
                'by_state': by_state,
                'total_rx_volume': total_volume,
                'average_rx_volume': total_volume / total_count if total_count > 0 else 0
            }
            
        except APIError:
            raise
        except Exception as e:
            error_msg = f"Failed to get API stats: {e}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
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