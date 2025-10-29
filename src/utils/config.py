"""Configuration management for Gorgias MCP Server."""

import os
import sys
from typing import Optional
from dotenv import load_dotenv


class GorgiasConfig:
    """Centralized configuration management for Gorgias MCP Server."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load .env file if it exists
        load_dotenv()
        
        # Load configuration values
        self.api_key = os.getenv("GORGIAS_API_KEY")
        self.username = os.getenv("GORGIAS_USERNAME")
        self.base_url = os.getenv("GORGIAS_BASE_URL", "https://petstoredirect.gorgias.com/api/")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate that all required configuration is present."""
        missing_vars = []
        
        if not self.api_key:
            missing_vars.append("GORGIAS_API_KEY")
        
        if not self.username:
            missing_vars.append("GORGIAS_USERNAME")
        
        if missing_vars:
            self._print_setup_instructions(missing_vars)
            sys.exit(1)
        
        # Additional validation
        if not self._is_valid_email(self.username):
            print("❌ Error: GORGIAS_USERNAME must be a valid email address")
            print(f"   Current value: {self.username}")
            sys.exit(1)
        
        if not self.base_url.startswith("https://"):
            print("❌ Error: GORGIAS_BASE_URL must start with https://")
            print(f"   Current value: {self.base_url}")
            sys.exit(1)
        
        if len(self.api_key) < 10:
            print("❌ Error: GORGIAS_API_KEY appears to be invalid (too short)")
            print(f"   Current value: {self.api_key[:5]}...")
            sys.exit(1)
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email.split("@")[-1]
    
    def _print_setup_instructions(self, missing_vars: list):
        """Print helpful setup instructions."""
        print("❌ Configuration Error")
        print("=" * 50)
        print()
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print()
        print("🔧 Setup Options:")
        print()
        print("1. Run the setup script:")
        print("   python setup.py")
        print()
        print("2. Set environment variables manually:")
        print("   export GORGIAS_API_KEY='your_api_key_here'")
        print("   export GORGIAS_USERNAME='your_email@example.com'")
        print("   export GORGIAS_BASE_URL='https://your-store.gorgias.com/api/'")
        print()
        print("3. Create a .env file:")
        print("   cp env.example .env")
        print("   # Then edit .env with your credentials")
        print()
        print("📖 For more help, see README.md")
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers for API requests."""
        import base64
        credentials = f"{self.username}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests."""
        return self.base_url.rstrip("/")
    
    def is_debug_enabled(self) -> bool:
        """Check if debug logging is enabled."""
        return self.debug
    
    def get_summary(self) -> dict:
        """Get a summary of the current configuration (without sensitive data)."""
        return {
            "username": self.username,
            "base_url": self.base_url,
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "debug_enabled": self.debug
        }


# Global configuration instance
config: Optional[GorgiasConfig] = None


def get_config() -> GorgiasConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = GorgiasConfig()
    return config

