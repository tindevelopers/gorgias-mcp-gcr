#!/bin/bash
set -e

echo "🚀 Starting Gorgias MCP Server Docker Container"

# Check if we're running in Railway (HTTP mode) or MCP mode
if [ "$RAILWAY_ENVIRONMENT" = "production" ] || [ "$RAILWAY_ENVIRONMENT" = "preview" ]; then
    echo "🌐 Running in Railway HTTP mode"
    echo "📡 Starting HTTP server for healthchecks"
    echo "⚠️  Note: MCP stdio functionality not available in Railway"
    python railway_http_mcp.py
else
    echo "🔧 Running in MCP stdio mode"
    echo "📡 Starting MCP server for stdio communication"
    python -m src.server
fi
