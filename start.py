#!/usr/bin/env python3
"""Railway startup script for Gorgias MCP Server."""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.server import main

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['GORGIAS_API_KEY', 'GORGIAS_USERNAME', 'GORGIAS_BASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these in your Railway environment variables")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting Gorgias MCP Server on Railway...")
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Start the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
