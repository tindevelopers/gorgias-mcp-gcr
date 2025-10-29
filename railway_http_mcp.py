#!/usr/bin/env python3
"""HTTP-based MCP server for Railway deployment with MCP protocol support."""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response

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
        if mcp_server is None:
            return web.Response(
                text=json.dumps({"status": "error", "message": "MCP server not initialized"}),
                status=503,
                content_type='application/json'
            )
        
        tools = mcp_server.get_all_tools()
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

async def mcp_initialize_handler(request):
    """Handle MCP initialize requests."""
    try:
        data = await request.json()
        logger.info(f"MCP Initialize request: {data}")
        
        response = {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "gorgias-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        
        return web.Response(
            text=json.dumps(response),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"MCP Initialize error: {e}")
        return web.Response(
            text=json.dumps({
                "jsonrpc": "2.0",
                "id": data.get("id") if 'data' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }),
            status=500,
            content_type='application/json'
        )

async def mcp_tools_list_handler(request):
    """Handle MCP tools/list requests."""
    try:
        data = await request.json()
        logger.info(f"MCP Tools List request: {data}")
        
        if mcp_server is None:
            return web.Response(
                text=json.dumps({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {"code": -32603, "message": "MCP server not initialized"}
                }),
                status=500,
                content_type='application/json'
            )
        
        tools = mcp_server.get_all_tools()
        tools_data = []
        
        for tool in tools:
            tools_data.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        
        response = {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "tools": tools_data
            }
        }
        
        return web.Response(
            text=json.dumps(response),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"MCP Tools List error: {e}")
        return web.Response(
            text=json.dumps({
                "jsonrpc": "2.0",
                "id": data.get("id") if 'data' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }),
            status=500,
            content_type='application/json'
        )

async def mcp_tools_call_handler(request):
    """Handle MCP tools/call requests."""
    try:
        data = await request.json()
        logger.info(f"MCP Tools Call request: {data}")
        
        if mcp_server is None:
            return web.Response(
                text=json.dumps({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {"code": -32603, "message": "MCP server not initialized"}
                }),
                status=500,
                content_type='application/json'
            )
        
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return web.Response(
                text=json.dumps({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {"code": -32602, "message": "Missing tool name"}
                }),
                status=400,
                content_type='application/json'
            )
        
        # Call the tool
        result = await mcp_server.handle_tool_call(tool_name, arguments)
        
        response = {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }
        
        return web.Response(
            text=json.dumps(response),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"MCP Tools Call error: {e}")
        return web.Response(
            text=json.dumps({
                "jsonrpc": "2.0",
                "id": data.get("id") if 'data' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }),
            status=500,
            content_type='application/json'
        )


async def mcp_resources_list_handler(request):
    """Handle MCP resources/list requests (stub)."""
    data = await request.json()
    response = {
        "jsonrpc": "2.0",
        "id": data.get("id"),
        "result": {
            "resources": []
        }
    }
    return web.Response(
        text=json.dumps(response),
        content_type='application/json'
    )


async def mcp_prompts_list_handler(request):
    """Handle MCP prompts/list requests (stub)."""
    data = await request.json()
    response = {
        "jsonrpc": "2.0",
        "id": data.get("id"),
        "result": {
            "prompts": []
        }
    }
    return web.Response(
        text=json.dumps(response),
        content_type='application/json'
    )


async def mcp_resources_read_handler(request):
    """Handle MCP resources/read requests (stub)."""
    data = await request.json()
    response = {
        "jsonrpc": "2.0",
        "id": data.get("id"),
        "error": {
            "code": -32601,
            "message": "resources/read is not supported"
        }
    }
    return web.Response(
        text=json.dumps(response),
        content_type='application/json'
    )


async def mcp_prompts_get_handler(request):
    """Handle MCP prompts/get requests (stub)."""
    data = await request.json()
    response = {
        "jsonrpc": "2.0",
        "id": data.get("id"),
        "error": {
            "code": -32601,
            "message": "prompts/get is not supported"
        }
    }
    return web.Response(
        text=json.dumps(response),
        content_type='application/json'
    )


async def mcp_handler(request):
    """Handle all MCP requests."""
    try:
        data = await request.json()
        method = data.get("method")
        
        if method == "initialize":
            return await mcp_initialize_handler(request)
        elif method == "tools/list":
            return await mcp_tools_list_handler(request)
        elif method == "tools/call":
            return await mcp_tools_call_handler(request)
        elif method == "resources/list":
            return await mcp_resources_list_handler(request)
        elif method == "resources/read":
            return await mcp_resources_read_handler(request)
        elif method == "prompts/list":
            return await mcp_prompts_list_handler(request)
        elif method == "prompts/get":
            return await mcp_prompts_get_handler(request)
        else:
            logger.warning(f"Unsupported MCP method requested: {method}")
            return web.Response(
                text=json.dumps({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }),
                content_type='application/json'
            )
    except Exception as e:
        logger.error(f"MCP Handler error: {e}")
        return web.Response(
            text=json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }),
            status=400,
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
    """Start the HTTP server with MCP endpoints."""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)
    app.router.add_post('/mcp', mcp_handler)
    
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 3000))
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"🌐 HTTP server started on port {port}")
    logger.info("📡 Healthcheck available at /health")
    logger.info("🔧 MCP endpoint available at /mcp")
    logger.info("📋 MCP clients can POST to /mcp with JSON-RPC requests")
    
    return runner

async def main():
    """Main function to start the HTTP MCP server."""
    logger.info("🚀 Starting Gorgias MCP Server on Railway...")
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Initialize MCP server
    if not await init_mcp_server():
        sys.exit(1)
    
    # Start HTTP server with MCP endpoints
    http_runner = await start_http_server()
    
    logger.info("✅ Gorgias MCP Server is ready!")
    logger.info("🔧 MCP functionality available via HTTP POST to /mcp")
    logger.info("🏥 Healthcheck endpoint available at /health")
    
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
