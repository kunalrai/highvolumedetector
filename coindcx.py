import os
import logging
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CoinDCXClient:
    def __init__(self):
        self.base_url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the CoinDCX API with error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log the response type and structure for debugging
            self.logger.debug(f"Response type: {type(data)}, Content preview: {str(data)[:200]}")
            
            return data
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            raise
    
    def get_active_pairs(self) -> List[Dict]:
        """Fetch all active futures trading pairs"""
        self.logger.info("Fetching active futures pairs")
        response = self._make_request("active_instruments")
        
        # Handle both list of strings and list of dicts
        if isinstance(response, list):
            # If any item is not a dict, assume it's a pair name string
            if response and not isinstance(response[0], dict):
                self.logger.info("Received list of strings, converting to pair objects")
                return [{"pair": str(pair)} for pair in response]
            return response
        else:
            self.logger.error(f"Unexpected response format: {type(response)}")
            raise ValueError(f"Expected list response, got {type(response)}")
    
    def get_pair_details(self, pair_name: str) -> Dict:
        """Fetch details for a specific trading pair"""
        self.logger.info(f"Fetching details for pair: {pair_name}")
        response = self._make_request("instrument", {"pair": pair_name})
        
        # Debug log the response
        self.logger.debug(f"Raw response for pair {pair_name}: {response}")
        
        # Handle different response formats
        if isinstance(response, list) and response:
            self.logger.info(f"Received list response for pair {pair_name}, using first item")
            return response[0] if isinstance(response[0], dict) else {"pair": str(response[0])}
        elif isinstance(response, dict):
            return response
        elif isinstance(response, str):
            self.logger.info(f"Received string response for pair {pair_name}")
            return {"pair": response}
        else:
            raise ValueError(f"Unexpected response format for pair {pair_name}: {response}")
        
    def __del__(self):
        """Clean up the session on deletion"""
        self.session.close()
