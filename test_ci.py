#!/usr/bin/env python3
"""Simple test script for CI/CD pipeline."""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.server import GorgiasMCPServer
        print("✅ GorgiasMCPServer import successful")
    except Exception as e:
        print(f"❌ GorgiasMCPServer import failed: {e}")
        return False
    
    try:
        from src.utils.auth import GorgiasAuth
        print("✅ GorgiasAuth import successful")
    except Exception as e:
        print(f"❌ GorgiasAuth import failed: {e}")
        return False
    
    try:
        from src.utils.api_client import GorgiasAPIClient
        print("✅ GorgiasAPIClient import successful")
    except Exception as e:
        print(f"❌ GorgiasAPIClient import failed: {e}")
        return False
    
    try:
        from src.tools.customers import CustomerTools
        print("✅ CustomerTools import successful")
    except Exception as e:
        print(f"❌ CustomerTools import failed: {e}")
        return False
    
    try:
        from src.tools.tickets import TicketTools
        print("✅ TicketTools import successful")
    except Exception as e:
        print(f"❌ TicketTools import failed: {e}")
        return False
    
    try:
        from railway_server import check_environment, init_mcp_server
        print("✅ Railway server imports successful")
    except Exception as e:
        print(f"❌ Railway server imports failed: {e}")
        return False
    
    return True

def test_server_initialization():
    """Test server initialization with mock credentials."""
    print("\n🔍 Testing server initialization...")
    
    # Set mock environment variables
    os.environ['GORGIAS_API_KEY'] = 'test_key_for_ci'
    os.environ['GORGIAS_USERNAME'] = 'test@example.com'
    os.environ['GORGIAS_BASE_URL'] = 'https://test.gorgias.com/api/'
    
    try:
        from src.server import GorgiasMCPServer
        server = GorgiasMCPServer()
        tools = server.get_all_tools()
        
        print(f"✅ Server initialized with {len(tools)} tools")
        print(f"Tools: {[tool.name for tool in tools]}")
        
        # Verify we have the expected tools
        expected_tools = [
            'list_customers', 'get_customer', 'create_customer', 'update_customer',
            'search_customers', 'get_customer_tickets', 'list_tickets', 'get_ticket',
            'create_ticket', 'update_ticket', 'search_tickets'
        ]
        
        tool_names = [tool.name for tool in tools]
        for expected_tool in expected_tools:
            if expected_tool not in tool_names:
                print(f"❌ Missing expected tool: {expected_tool}")
                return False
        
        print("✅ All expected tools are present")
        return True
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

def test_environment_check():
    """Test environment variable checking."""
    print("\n🔍 Testing environment check...")
    
    try:
        from railway_server import check_environment
        
        # Test with valid environment
        if check_environment():
            print("✅ Environment check passed with valid variables")
        else:
            print("❌ Environment check failed with valid variables")
            return False
        
        # Test with missing environment
        original_key = os.environ.get('GORGIAS_API_KEY')
        del os.environ['GORGIAS_API_KEY']
        
        if not check_environment():
            print("✅ Environment check correctly failed with missing variables")
        else:
            print("❌ Environment check should have failed with missing variables")
            return False
        
        # Restore environment
        if original_key:
            os.environ['GORGIAS_API_KEY'] = original_key
        
        return True
        
    except Exception as e:
        print(f"❌ Environment check test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration files are valid."""
    print("\n🔍 Testing configuration files...")
    
    try:
        import json
        
        # Test railway.json
        with open('railway.json', 'r') as f:
            railway_config = json.load(f)
        
        assert railway_config['build']['builder'] == 'NIXPACKS'
        assert railway_config['deploy']['startCommand'] == 'python railway_server.py'
        print("✅ railway.json is valid")
        
        # Test mcp_config.json
        with open('mcp_config.json', 'r') as f:
            mcp_config = json.load(f)
        
        assert 'mcpServers' in mcp_config
        assert 'gorgias' in mcp_config['mcpServers']
        print("✅ mcp_config.json is valid")
        
        # Test requirements.txt
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        assert 'mcp>=' in requirements
        assert 'aiohttp>=' in requirements
        print("✅ requirements.txt is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration files test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting CI tests for Gorgias MCP Server")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_server_initialization,
        test_environment_check,
        test_configuration_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed: {test.__name__}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print(f"🎉 All tests passed! ({passed}/{total})")
    print("✅ Gorgias MCP Server is ready for deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
