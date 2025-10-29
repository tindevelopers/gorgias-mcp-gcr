#!/usr/bin/env python3
"""Test script to verify MCP server setup."""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from src.server import GorgiasMCPServer
        from src.utils.auth import GorgiasAuth
        from src.utils.api_client import GorgiasAPIClient
        from src.tools.customers import CustomerTools
        from src.tools.tickets import TicketTools
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_initialization():
    """Test that the server can be initialized."""
    print("\n🔍 Testing server initialization...")
    try:
        from src.server import GorgiasMCPServer
        server = GorgiasMCPServer()
        print("✅ Server initialization successful")
        return True
    except Exception as e:
        print(f"❌ Server initialization error: {e}")
        return False

def test_environment_setup():
    """Test environment configuration."""
    print("\n🔍 Testing environment setup...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found - you'll need to create it with your Gorgias credentials")
    
    # Check environment variables
    required_vars = ["GORGIAS_API_KEY", "GORGIAS_USERNAME", "GORGIAS_BASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n📝 To set up your environment:")
        print("1. Copy env.example to .env: cp env.example .env")
        print("2. Edit .env with your actual Gorgias credentials")
        print("3. Or set environment variables:")
        for var in missing_vars:
            print(f"   export {var}='your_value_here'")
    
    return len(missing_vars) == 0

def test_mcp_config():
    """Test MCP configuration file."""
    print("\n🔍 Testing MCP configuration...")
    
    config_file = Path("mcp_config.json")
    if config_file.exists():
        print("✅ mcp_config.json exists")
        
        # Check if the working directory is correct
        import json
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            cwd = config.get("mcpServers", {}).get("gorgias", {}).get("cwd", "")
            current_dir = str(Path.cwd())
            
            if cwd == current_dir:
                print("✅ MCP config working directory is correct")
            else:
                print(f"⚠️  MCP config working directory mismatch:")
                print(f"   Config: {cwd}")
                print(f"   Current: {current_dir}")
                
        except Exception as e:
            print(f"❌ Error reading MCP config: {e}")
    else:
        print("❌ mcp_config.json not found")
        return False
    
    return True

async def test_tool_listing():
    """Test that tools can be listed."""
    print("\n🔍 Testing tool listing...")
    try:
        from src.server import GorgiasMCPServer
        server = GorgiasMCPServer()
        tools = server.get_all_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        return True
    except Exception as e:
        print(f"❌ Tool listing error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Gorgias MCP Server Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_server_initialization,
        test_environment_setup,
        test_mcp_config,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Run async test
    async_test_result = asyncio.run(test_tool_listing())
    results.append(async_test_result)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🎉 Your MCP server is ready to use!")
        print("\nNext steps:")
        print("1. Set up your Gorgias credentials in .env file")
        print("2. Run: python -m src.server")
        print("3. Or test with: python example_usage.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nSome issues need to be resolved before the server is ready.")

if __name__ == "__main__":
    main()
