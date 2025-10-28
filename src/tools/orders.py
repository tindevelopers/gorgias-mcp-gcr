"""Order management tools for Gorgias MCP server."""

from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from ..utils.api_client import GorgiasAPIClient


class OrderTools:
    """Tools for managing Gorgias orders."""
    
    def __init__(self, api_client: GorgiasAPIClient):
        """Initialize order tools with API client.
        
        Args:
            api_client: GorgiasAPIClient instance.
        """
        self.api_client = api_client
    
    def get_tools(self) -> List[Tool]:
        """Get list of order-related tools.
        
        Returns:
            List of Tool objects for order management.
        """
        return [
            Tool(
                name="list_orders",
                description="List all orders with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of orders to return",
                            "default": 50
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Filter by customer ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by order status"
                        },
                        "created_after": {
                            "type": "string",
                            "description": "Filter orders created after this date (ISO format)"
                        },
                        "created_before": {
                            "type": "string",
                            "description": "Filter orders created before this date (ISO format)"
                        }
                    }
                }
            ),
            Tool(
                name="get_order",
                description="Get details of a specific order",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "ID of the order to retrieve"
                        }
                    },
                    "required": ["order_id"]
                }
            ),
            Tool(
                name="search_orders",
                description="Search orders by customer, order number, or other criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_customer_orders",
                description="Get all orders for a specific customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of orders to return",
                            "default": 50
                        }
                    },
                    "required": ["customer_id"]
                }
            ),
            Tool(
                name="get_order_metrics",
                description="Get order statistics and metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "description": "Time period for metrics",
                            "enum": ["day", "week", "month", "year"],
                            "default": "month"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for metrics (ISO format)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for metrics (ISO format)"
                        }
                    }
                }
            )
        ]
    
    async def list_orders(self, **kwargs) -> str:
        """List orders with optional filtering.
        
        Args:
            **kwargs: Filter parameters.
            
        Returns:
            JSON string of orders data.
        """
        try:
            # Build query parameters
            params = {}
            if "limit" in kwargs:
                params["limit"] = kwargs["limit"]
            if "customer_id" in kwargs:
                params["customer_id"] = kwargs["customer_id"]
            if "status" in kwargs:
                params["status"] = kwargs["status"]
            if "created_after" in kwargs:
                params["created_after"] = kwargs["created_after"]
            if "created_before" in kwargs:
                params["created_before"] = kwargs["created_before"]
            
            response = await self.api_client.get("orders", params=params)
            return f"Found {len(response.get('data', []))} orders:\n{response}"
            
        except Exception as e:
            return f"Error listing orders: {str(e)}"
    
    async def get_order(self, order_id: int) -> str:
        """Get details of a specific order.
        
        Args:
            order_id: ID of the order to retrieve.
            
        Returns:
            JSON string of order data.
        """
        try:
            response = await self.api_client.get(f"orders/{order_id}")
            return f"Order {order_id} details:\n{response}"
            
        except Exception as e:
            return f"Error getting order {order_id}: {str(e)}"
    
    async def search_orders(self, query: str, limit: int = 50) -> str:
        """Search orders by customer, order number, or other criteria.
        
        Args:
            query: Search query.
            limit: Maximum number of results.
            
        Returns:
            JSON string of search results.
        """
        try:
            params = {
                "q": query,
                "limit": limit
            }
            
            response = await self.api_client.get("orders/search", params=params)
            return f"Found {len(response.get('data', []))} orders matching '{query}':\n{response}"
            
        except Exception as e:
            return f"Error searching orders: {str(e)}"
    
    async def get_customer_orders(self, customer_id: int, limit: int = 50) -> str:
        """Get all orders for a specific customer.
        
        Args:
            customer_id: ID of the customer.
            limit: Maximum number of orders to return.
            
        Returns:
            JSON string of customer orders.
        """
        try:
            params = {
                "customer_id": customer_id,
                "limit": limit
            }
            
            response = await self.api_client.get("orders", params=params)
            return f"Found {len(response.get('data', []))} orders for customer {customer_id}:\n{response}"
            
        except Exception as e:
            return f"Error getting orders for customer {customer_id}: {str(e)}"
    
    async def get_order_metrics(self, **kwargs) -> str:
        """Get order statistics and metrics.
        
        Args:
            **kwargs: Metrics parameters.
            
        Returns:
            JSON string of order metrics.
        """
        try:
            # Build query parameters
            params = {}
            if "period" in kwargs:
                params["period"] = kwargs["period"]
            if "start_date" in kwargs:
                params["start_date"] = kwargs["start_date"]
            if "end_date" in kwargs:
                params["end_date"] = kwargs["end_date"]
            
            response = await self.api_client.get("orders/metrics", params=params)
            return f"Order metrics:\n{response}"
            
        except Exception as e:
            return f"Error getting order metrics: {str(e)}"


