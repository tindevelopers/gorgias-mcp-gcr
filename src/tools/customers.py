"""Customer management tools for Gorgias MCP server."""

from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from ..utils.api_client import GorgiasAPIClient


class CustomerTools:
    """Tools for managing Gorgias customers."""
    
    def __init__(self, api_client: GorgiasAPIClient):
        """Initialize customer tools with API client.
        
        Args:
            api_client: GorgiasAPIClient instance.
        """
        self.api_client = api_client
    
    def get_tools(self) -> List[Tool]:
        """Get list of customer-related tools.
        
        Returns:
            List of Tool objects for customer management.
        """
        return [
            Tool(
                name="list_customers",
                description="List all customers with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of customers to return",
                            "default": 50
                        },
                        "email": {
                            "type": "string",
                            "description": "Filter by customer email"
                        },
                        "created_after": {
                            "type": "string",
                            "description": "Filter customers created after this date (ISO format)"
                        },
                        "created_before": {
                            "type": "string",
                            "description": "Filter customers created before this date (ISO format)"
                        }
                    }
                }
            ),
            Tool(
                name="get_customer",
                description="Get details of a specific customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer to retrieve"
                        }
                    },
                    "required": ["customer_id"]
                }
            ),
            Tool(
                name="create_customer",
                description="Create a new customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Customer email address"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Customer first name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Customer last name"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "language": {
                            "type": "string",
                            "description": "Customer language preference"
                        }
                    },
                    "required": ["email"]
                }
            ),
            Tool(
                name="update_customer",
                description="Update an existing customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer to update"
                        },
                        "email": {
                            "type": "string",
                            "description": "New customer email"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "New customer first name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "New customer last name"
                        },
                        "phone": {
                            "type": "string",
                            "description": "New customer phone number"
                        },
                        "language": {
                            "type": "string",
                            "description": "New customer language preference"
                        }
                    },
                    "required": ["customer_id"]
                }
            ),
            Tool(
                name="search_customers",
                description="Search customers by email, name, or other criteria",
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
                name="get_customer_tickets",
                description="Get all tickets for a specific customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tickets to return",
                            "default": 50
                        }
                    },
                    "required": ["customer_id"]
                }
            )
        ]
    
    async def list_customers(self, **kwargs) -> str:
        """List customers with optional filtering.
        
        Args:
            **kwargs: Filter parameters.
            
        Returns:
            JSON string of customers data.
        """
        try:
            # Build query parameters
            params = {}
            if "limit" in kwargs:
                params["limit"] = kwargs["limit"]
            if "email" in kwargs:
                params["email"] = kwargs["email"]
            if "created_after" in kwargs:
                params["created_after"] = kwargs["created_after"]
            if "created_before" in kwargs:
                params["created_before"] = kwargs["created_before"]
            
            response = await self.api_client.get("customers", params=params)
            return f"Found {len(response.get('data', []))} customers:\n{response}"
            
        except Exception as e:
            return f"Error listing customers: {str(e)}"
    
    async def get_customer(self, customer_id: int) -> str:
        """Get details of a specific customer.
        
        Args:
            customer_id: ID of the customer to retrieve.
            
        Returns:
            JSON string of customer data.
        """
        try:
            response = await self.api_client.get(f"customers/{customer_id}")
            return f"Customer {customer_id} details:\n{response}"
            
        except Exception as e:
            return f"Error getting customer {customer_id}: {str(e)}"
    
    async def create_customer(self, **kwargs) -> str:
        """Create a new customer.
        
        Args:
            **kwargs: Customer creation parameters.
            
        Returns:
            JSON string of created customer data.
        """
        try:
            # Build customer data
            customer_data = {
                "email": kwargs["email"]
            }
            
            if "first_name" in kwargs:
                customer_data["first_name"] = kwargs["first_name"]
            if "last_name" in kwargs:
                customer_data["last_name"] = kwargs["last_name"]
            if "phone" in kwargs:
                customer_data["phone"] = kwargs["phone"]
            if "language" in kwargs:
                customer_data["language"] = kwargs["language"]
            
            response = await self.api_client.post("customers", data=customer_data)
            return f"Created customer {response.get('id', 'unknown')}:\n{response}"
            
        except Exception as e:
            return f"Error creating customer: {str(e)}"
    
    async def update_customer(self, customer_id: int, **kwargs) -> str:
        """Update an existing customer.
        
        Args:
            customer_id: ID of the customer to update.
            **kwargs: Update parameters.
            
        Returns:
            JSON string of updated customer data.
        """
        try:
            # Build update data
            update_data = {}
            if "email" in kwargs:
                update_data["email"] = kwargs["email"]
            if "first_name" in kwargs:
                update_data["first_name"] = kwargs["first_name"]
            if "last_name" in kwargs:
                update_data["last_name"] = kwargs["last_name"]
            if "phone" in kwargs:
                update_data["phone"] = kwargs["phone"]
            if "language" in kwargs:
                update_data["language"] = kwargs["language"]
            
            response = await self.api_client.put(f"customers/{customer_id}", data=update_data)
            return f"Updated customer {customer_id}:\n{response}"
            
        except Exception as e:
            return f"Error updating customer {customer_id}: {str(e)}"
    
    async def search_customers(self, query: str, limit: int = 50) -> str:
        """Search customers by email, name, or other criteria.
        
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
            
            response = await self.api_client.get("customers/search", params=params)
            return f"Found {len(response.get('data', []))} customers matching '{query}':\n{response}"
            
        except Exception as e:
            return f"Error searching customers: {str(e)}"
    
    async def get_customer_tickets(self, customer_id: int, limit: int = 50) -> str:
        """Get all tickets for a specific customer.
        
        Args:
            customer_id: ID of the customer.
            limit: Maximum number of tickets to return.
            
        Returns:
            JSON string of customer tickets.
        """
        try:
            params = {
                "customer_id": customer_id,
                "limit": limit
            }
            
            response = await self.api_client.get("tickets", params=params)
            return f"Found {len(response.get('data', []))} tickets for customer {customer_id}:\n{response}"
            
        except Exception as e:
            return f"Error getting tickets for customer {customer_id}: {str(e)}"


