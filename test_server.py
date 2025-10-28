#!/usr/bin/env python3
"""Test script for the Gorgias MCP Server."""

import asyncio
import sys
import os
import types

# Ensure project root is on PYTHONPATH for package imports
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Provide minimal MCP stubs for offline testing if the real package isn't installed
try:
    import mcp  # type: ignore
except ModuleNotFoundError:
    mcp = types.ModuleType("mcp")
    mcp_server_mod = types.ModuleType("mcp.server")
    mcp_types_mod = types.ModuleType("mcp.types")

    class _Tool:
        def __init__(self, name, description="", inputSchema=None):
            self.name = name
            self.description = description
            self.inputSchema = inputSchema or {}

    class _TextContent:
        def __init__(self, type, text):
            self.type = type
            self.text = text

    class _Server:
        def __init__(self, name: str):
            self.name = name
        def list_tools(self):
            def decorator(fn):
                return fn
            return decorator
        def call_tool(self):
            def decorator(fn):
                return fn
            return decorator
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def run(self):
            return None

    mcp_server_mod.Server = _Server
    mcp_types_mod.Tool = _Tool
    mcp_types_mod.TextContent = _TextContent

    sys.modules["mcp"] = mcp
    sys.modules["mcp.server"] = mcp_server_mod
    sys.modules["mcp.types"] = mcp_types_mod

from src.server import GorgiasMCPServer


async def test_server_initialization():
    """Test that the server can be initialized."""
    print("Testing server initialization...")
    
    try:
        # Ensure env vars are set for initialization without real secrets
        os.environ.setdefault("GORGIAS_API_KEY", "test")
        os.environ.setdefault("GORGIAS_BASE_URL", "https://example.com/api/")
        server = GorgiasMCPServer()
        print("✅ Server initialized successfully")
        
        # Test getting tools
        tools = server.get_all_tools()
        print(f"✅ Found {len(tools)} tools")
        
        # List tool names
        tool_names = [tool.name for tool in tools]
        print(f"Available tools: {', '.join(tool_names)}")
        
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False


async def test_tool_calls():
    """Test tool calls (without actual API calls)."""
    print("\nTesting tool calls...")
    
    try:
        # Ensure env vars are set for initialization without real secrets
        os.environ.setdefault("GORGIAS_API_KEY", "test")
        os.environ.setdefault("GORGIAS_BASE_URL", "https://example.com/api/")
        server = GorgiasMCPServer()
        
        # Stub network calls to avoid real HTTP requests
        async def fake_get(self, endpoint, params=None):
            return {"data": []}
        
        server.api_client.get = types.MethodType(fake_get, server.api_client)
        
        # Test a tool call that should fail gracefully without API key
        result = await server.handle_tool_call("list_customers", {"limit": 1})
        print(f"Tool call result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Tool call test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Running Gorgias MCP Server tests...\n")
    
    # Test 1: Server initialization
    init_success = await test_server_initialization()
    
    # Test 2: Tool calls
    tool_success = await test_tool_calls()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"  Server initialization: {'✅ PASS' if init_success else '❌ FAIL'}")
    print(f"  Tool calls: {'✅ PASS' if tool_success else '❌ FAIL'}")
    
    if init_success and tool_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
