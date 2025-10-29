"""Authentication utilities for Gorgias API."""

from typing import Optional
from .config import get_config


class GorgiasAuth:
    """Handles authentication for Gorgias API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, username: Optional[str] = None):
        """Initialize authentication with API key, base URL, and username.
        
        Args:
            api_key: Gorgias API key. If not provided, will use global config.
            base_url: Gorgias API base URL. If not provided, will use global config.
            username: Gorgias username/email. If not provided, will use global config.
        """
        # Use global config if no specific values provided
        if api_key is None and base_url is None and username is None:
            config = get_config()
            self.api_key = config.api_key
            self.base_url = config.base_url
            self.username = config.username
        else:
            # Use provided values or fall back to config
            config = get_config()
            self.api_key = api_key or config.api_key
            self.base_url = base_url or config.base_url
            self.username = username or config.username
    
    def get_headers(self) -> dict:
        """Get authentication headers for API requests.
        
        Returns:
            Dictionary containing authentication headers.
        """
        import base64
        credentials = f"{self.username}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests.
        
        Returns:
            The base URL for Gorgias API.
        """
        return self.base_url.rstrip("/")


