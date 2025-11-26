#!/usr/bin/env python3
"""HTTP-based MCP server for Google Cloud Run with streaming support."""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from aiohttp import web

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.server import GorgiasMCPServer  # noqa: E402

# Configure logging for Cloud Run
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
        logger.error("Please set these in your Cloud Run environment variables")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

async def healthcheck_handler(request):
    """Handle Cloud Run healthcheck requests."""
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
                "environment": os.getenv("RAILWAY_ENVIRONMENT", "cloud-run"),
                "tools_count": len(tools),
                "tools": [tool.name for tool in tools],
                "streaming": True
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
                    "tools": {},
                    "streaming": True  # Indicate streaming support
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
    """Handle MCP tools/call requests with streaming support."""
    try:
        data = await request.json()
        logger.info(f"MCP Tools Call request: {data}")
        
        # Check if client wants streaming
        params = data.get("params", {})
        stream = params.get("stream", False)
        
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
        
        # If streaming requested, use SSE
        if stream:
            return await stream_tool_call(request, tool_name, arguments, data.get("id"))
        
        # Otherwise, return standard response
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

async def stream_tool_call(request, tool_name, arguments, request_id):
    """Stream tool call results using Server-Sent Events (SSE)."""
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # Disable buffering for Cloud Run
        }
    )
    
    await response.prepare(request)
    
    try:
        # Send initial status
        initial_message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Starting {tool_name}..."
                    }
                ]
            }
        }
        await response.write(f"data: {json.dumps(initial_message)}\n\n".encode())
        
        # Call the tool (this is async, so we can stream progress)
        # For now, we'll stream the result in chunks
        result = await mcp_server.handle_tool_call(tool_name, arguments)
        
        # Stream result in chunks for better UX
        chunk_size = 500  # Characters per chunk
        result_chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
        
        accumulated_text = ""
        for i, chunk in enumerate(result_chunks):
            accumulated_text += chunk
            chunk_message = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": accumulated_text
                        }
                    ]
                }
            }
            await response.write(f"data: {json.dumps(chunk_message)}\n\n".encode())
            await asyncio.sleep(0.01)  # Small delay for streaming effect
        
        # Send final completion message (optional, some clients don't need it)
        # The complete result is already sent in the last chunk
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        error_message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }
        await response.write(f"data: {json.dumps(error_message)}\n\n".encode())
    finally:
        await response.write_eof()
    
    return response

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
    
    # Add CORS headers for Cloud Run
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
    
    # Add routes
    app.router.add_get('/', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)
    app.router.add_post('/mcp', mcp_handler)
    app.router.add_options('/mcp', lambda r: web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }))
    
    # Get port from Cloud Run environment (PORT is set by Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"🌐 HTTP server started on port {port}")
    logger.info("📡 Healthcheck available at /health")
    logger.info("🔧 MCP endpoint available at /mcp")
    logger.info("📋 MCP clients can POST to /mcp with JSON-RPC requests")
    logger.info("🌊 Streaming support enabled (use stream: true in params)")
    
    return runner

async def main():
    """Main function to start the HTTP MCP server."""
    logger.info("🚀 Starting Gorgias MCP Server on Google Cloud Run...")
    
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
    logger.info("🌊 Streaming available (set stream: true in request params)")
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

