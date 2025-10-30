"""Main MCP server for Gorgias integration."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .utils.auth import GorgiasAuth
from .utils.api_client import GorgiasAPIClient
from .tools.customers import CustomerTools
from .tools.tickets import TicketTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("gorgias-mcp-server")


class GorgiasMCPServer:
    """Main MCP server class for Gorgias integration."""
    
    def __init__(self):
        """Initialize the MCP server with all tools."""
        self.auth = None
        self.api_client = None
        self.customer_tools = None
        self.ticket_tools = None
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize authentication and all tool classes."""
        try:
            self.auth = GorgiasAuth()
            self.api_client = GorgiasAPIClient(self.auth)
            self.customer_tools = CustomerTools(self.api_client)
            self.ticket_tools = TicketTools(self.api_client)
            logger.info("Successfully initialized Gorgias MCP server")
        except Exception as e:
            logger.error(f"Failed to initialize Gorgias MCP server: {e}")
            raise
    
    def get_all_tools(self) -> List[Tool]:
        """Get all available tools from all tool classes.
        
        Returns:
            List of all available Tool objects.
        """
        tools = []
        if self.customer_tools:
            tools.extend(self.customer_tools.get_tools())
        if self.ticket_tools:
            tools.extend(self.ticket_tools.get_tools())
        return tools
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> str:
        """Handle tool calls by routing to appropriate tool class.
        
        Args:
            name: Name of the tool to call.
            arguments: Arguments for the tool.
            
        Returns:
            Result of the tool execution.
        """
        try:
            # Route to customer tools
            if name.startswith(("list_customers", "get_customer", "create_customer", 
                              "update_customer", "search_customers", "get_customer_tickets")):
                if not self.customer_tools:
                    return "Customer tools not available"
                
                method = getattr(self.customer_tools, name)
                return await method(**arguments)
            
            # Route to ticket tools
            elif name.startswith(("list_tickets", "get_ticket", "create_ticket", 
                                "update_ticket", "search_tickets")):
                if not self.ticket_tools:
                    return "Ticket tools not available"
                
                method = getattr(self.ticket_tools, name)
                return await method(**arguments)
            
            elif name == "add_customer_email":
                if not self.customer_tools:
                    return "Customer tools not available"
                
                method = getattr(self.customer_tools, name)
                return await method(**arguments)
            
            else:
                return f"Unknown tool: {name}"
                
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return f"Error executing tool {name}: {str(e)}"


# Lazily-initialized server instance
gorgias_server: Optional[GorgiasMCPServer] = None


def _get_server() -> GorgiasMCPServer:
    """Get or initialize the global GorgiasMCPServer instance."""
    global gorgias_server
    if gorgias_server is None:
        gorgias_server = GorgiasMCPServer()
    return gorgias_server


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools.
    
    Returns:
        List of all available Tool objects.
    """
    return _get_server().get_all_tools()


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Call a tool by name with arguments.
    
    Args:
        name: Name of the tool to call.
        arguments: Arguments for the tool.
        
    Returns:
        List containing the result as TextContent.
    """
    result = await _get_server().handle_tool_call(name, arguments)
    return [TextContent(type="text", text=result)]


async def main():
    """Main entry point for the MCP server."""
    try:
        # Run the server with stdio
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                None  # initialization_options
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
