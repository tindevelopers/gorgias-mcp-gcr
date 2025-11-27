#!/bin/bash
set -e

echo "🚀 Starting Gorgias MCP Server Docker Container"

# Check if PORT is set (Cloud Run HTTP mode) or use stdio mode
if [ -n "$PORT" ]; then
    echo "🌐 Running in Cloud Run HTTP mode"
    echo "📡 Starting HTTP server with streaming support"
    echo "🔧 MCP endpoint available at /mcp"
    python cloud_run_mcp.py
else
    echo "🔧 Running in MCP stdio mode"
    echo "📡 Starting MCP server for stdio communication"
    python -m src.server
fi
