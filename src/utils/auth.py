"""Authentication utilities for Gorgias API."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GorgiasAuth:
    """Handles authentication for Gorgias API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize authentication with API key and base URL.
        
        Args:
            api_key: Gorgias API key. If not provided, will try to get from environment.
            base_url: Gorgias API base URL. If not provided, will use default.
        """
        self.api_key = api_key or os.getenv("GORGIAS_API_KEY")
        self.base_url = base_url or os.getenv("GORGIAS_BASE_URL", "https://petstoredirect.gorgias.com/api/")
        
        if not self.api_key:
            raise ValueError("Gorgias API key is required. Set GORGIAS_API_KEY environment variable or pass api_key parameter.")
    
    def get_headers(self) -> dict:
        """Get authentication headers for API requests.
        
        Returns:
            Dictionary containing authentication headers.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests.
        
        Returns:
            The base URL for Gorgias API.
        """
        return self.base_url.rstrip("/")


