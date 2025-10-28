#!/usr/bin/env python3
"""Example usage of the Gorgias MCP Server."""

import asyncio
import os
from src.server import GorgiasMCPServer


async def main():
    """Example of using the Gorgias MCP Server."""
    # Check if environment variables are set
    if not os.getenv("GORGIAS_API_KEY"):
        print("Please set GORGIAS_API_KEY environment variable")
        return
    
    # Initialize the server
    try:
        server = GorgiasMCPServer()
        print("✅ Gorgias MCP Server initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        return
    
    # Example 1: List customers
    print("\n📋 Listing customers...")
    try:
        result = await server.handle_tool_call("list_customers", {"limit": 5})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: List tickets
    print("\n🎫 Listing tickets...")
    try:
        result = await server.handle_tool_call("list_tickets", {"limit": 5})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: List orders
    print("\n📦 Listing orders...")
    try:
        result = await server.handle_tool_call("list_orders", {"limit": 5})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Search customers
    print("\n🔍 Searching customers...")
    try:
        result = await server.handle_tool_call("search_customers", {"query": "test", "limit": 3})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())


