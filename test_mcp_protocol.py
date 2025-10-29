#!/usr/bin/env python3
"""Test script to verify MCP protocol functionality."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_protocol():
    """Test the MCP protocol by sending proper JSON-RPC messages."""
    print("🧪 Testing MCP Protocol")
    print("=" * 50)
    
    # Set up environment
    env = {
        "GORGIAS_API_KEY": "a9030dea3e101a8f7d7565dcf02f376790967e602a49df0ac2a7fb5159c9c62d",
        "GORGIAS_USERNAME": "ai-developer@tin.info", 
        "GORGIAS_BASE_URL": "https://petstoredirect.gorgias.com/api/"
    }
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, "-m", "src.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**env, **os.environ}
    )
    
    try:
        # Step 1: Initialize
        print("1️⃣ Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"   Response: {json.dumps(response, indent=2)}")
            
            if "error" in response:
                print("❌ Initialize failed")
                return False
            else:
                print("✅ Initialize successful")
        
        # Step 2: List tools
        print("\n2️⃣ Sending tools/list request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"   Response: {json.dumps(response, indent=2)}")
            
            if "error" in response:
                print("❌ Tools list failed")
                return False
            else:
                tools = response.get("result", {}).get("tools", [])
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i:2d}. {tool['name']}: {tool['description']}")
                return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    import os
    success = asyncio.run(test_mcp_protocol())
    sys.exit(0 if success else 1)
