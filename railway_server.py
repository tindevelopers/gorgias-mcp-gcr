#!/usr/bin/env python3
"""Railway-optimized server with HTTP healthcheck support."""

import os
import sys
import asyncio
import logging
from pathlib import Path
from aiohttp import web, ClientSession
import json

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.server import GorgiasMCPServer

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global MCP server instance
mcp_server = None

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

async def healthcheck_handler(request):
    """Handle Railway healthcheck requests."""
    try:
        # Check if MCP server is initialized
        if mcp_server is None:
            return web.Response(
                text=json.dumps({"status": "error", "message": "MCP server not initialized"}),
                status=503,
                content_type='application/json'
            )
        
        # Test basic functionality
        tools = mcp_server.get_all_tools()
        if len(tools) == 0:
            return web.Response(
                text=json.dumps({"status": "error", "message": "No tools available"}),
                status=503,
                content_type='application/json'
            )
        
        return web.Response(
            text=json.dumps({
                "status": "healthy",
                "message": "Gorgias MCP Server is running",
                "tools_count": len(tools),
                "tools": [tool.name for tool in tools]
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Healthcheck error: {e}")
        return web.Response(
            text=json.dumps({"status": "error", "message": str(e)}),
            status=503,
            content_type='application/json'
        )

async def status_handler(request):
    """Handle status requests."""
    return web.Response(
        text=json.dumps({
            "service": "Gorgias MCP Server",
            "status": "running",
            "environment": "railway",
            "version": "1.0.0"
        }),
        content_type='application/json'
    )

async def init_mcp_server():
    """Initialize the MCP server."""
    global mcp_server
    try:
        mcp_server = GorgiasMCPServer()
        logger.info("✅ MCP server initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        return False

async def start_http_server():
    """Start the HTTP server for healthchecks."""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)
    app.router.add_get('/status', status_handler)
    
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 3000))
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"🌐 HTTP server started on port {port}")
    logger.info("📡 Healthcheck available at /health")
    logger.info("📊 Status available at /status")
    
    return runner

async def main():
    """Main function to start both HTTP server and MCP server."""
    logger.info("🚀 Starting Gorgias MCP Server on Railway...")
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Initialize MCP server
    if not await init_mcp_server():
        sys.exit(1)
    
    # Start HTTP server for healthchecks
    http_runner = await start_http_server()
    
    logger.info("✅ Gorgias MCP Server is ready!")
    logger.info("🔧 MCP functionality available via stdio")
    logger.info("🏥 Healthcheck endpoint available via HTTP")
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        await http_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
