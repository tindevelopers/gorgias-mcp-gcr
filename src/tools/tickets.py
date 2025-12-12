"""Ticket management tools for Gorgias MCP server."""

import json
import os
from typing import Any, List, Optional
from mcp.types import Tool
from ..utils.api_client import GorgiasAPIClient


class TicketTools:
    """Tools for managing Gorgias tickets."""
    
    def __init__(self, api_client: GorgiasAPIClient):
        """Initialize ticket tools with API client.
        
        Args:
            api_client: GorgiasAPIClient instance.
        """
        self.api_client = api_client
    
    def get_tools(self) -> List[Tool]:
        """Get list of ticket-related tools.
        
        Returns:
            List of Tool objects for ticket management.
        """
        return [
            Tool(
                name="list_tickets",
                description="List all tickets with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tickets to return",
                            "default": 50
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by ticket status",
                            "enum": ["open", "closed", "pending", "solved"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by ticket priority",
                            "enum": ["low", "normal", "high", "urgent"]
                        },
                        "assignee_id": {
                            "type": "integer",
                            "description": "Filter by assignee ID"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Filter by customer ID"
                        }
                    }
                }
            ),
            Tool(
                name="get_ticket",
                description="Get details of a specific ticket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID of the ticket to retrieve"
                        }
                    },
                    "required": ["ticket_id"]
                }
            ),
            Tool(
                name="create_ticket",
                description="Create a new support ticket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Ticket subject"
                        },
                        "body": {
                            "type": "string",
                            "description": "Ticket body content"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer creating the ticket"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Ticket priority",
                            "enum": ["low", "normal", "high", "urgent"],
                            "default": "normal"
                        },
                        "assignee_id": {
                            "type": "integer",
                            "description": "ID of the agent to assign the ticket to"
                        },
                        "tags": {
                            "type": "array",
                            "description": "List of tag names to apply to the ticket",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["subject", "body", "customer_id"]
                }
            ),
            Tool(
                name="update_ticket",
                description="Update an existing ticket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "integer",
                            "description": "ID of the ticket to update"
                        },
                        "status": {
                            "type": "string",
                            "description": "New ticket status",
                            "enum": ["open", "closed", "pending", "solved"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "New ticket priority",
                            "enum": ["low", "normal", "high", "urgent"]
                        },
                        "assignee_id": {
                            "type": "integer",
                            "description": "New assignee ID"
                        },
                        "subject": {
                            "type": "string",
                            "description": "New ticket subject"
                        }
                    },
                    "required": ["ticket_id"]
                }
            ),
            Tool(
                name="search_tickets",
                description="Search tickets by content, customer, or other criteria",
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
            )
        ]
    
    def _format_json(self, data: Any) -> str:
        """Format data as a pretty-printed JSON string."""
        try:
            return json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError):
            return str(data)

    async def list_tickets(self, **kwargs) -> str:
        """List tickets with optional filtering.
        
        Args:
            **kwargs: Filter parameters.
            
        Returns:
            JSON string of tickets data.
        """
        try:
            # Build query parameters
            params = {}
            if "limit" in kwargs:
                params["limit"] = kwargs["limit"]
            if "status" in kwargs:
                params["status"] = kwargs["status"]
            if "priority" in kwargs:
                params["priority"] = kwargs["priority"]
            if "assignee_id" in kwargs:
                params["assignee_id"] = kwargs["assignee_id"]
            if "customer_id" in kwargs:
                params["customer_id"] = kwargs["customer_id"]
            
            data = await self.api_client.get("tickets", params=params)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return f"Found {count} tickets:\n{self._format_json(data)}"
            
        except Exception as e:
            return f"Error listing tickets: {str(e)}"
    
    async def get_ticket(self, ticket_id: int) -> str:
        """Get details of a specific ticket.
        
        Args:
            ticket_id: ID of the ticket to retrieve.
            
        Returns:
            JSON string of ticket data.
        """
        try:
            data = await self.api_client.get(f"tickets/{ticket_id}")
            return f"Ticket {ticket_id} details:\n{self._format_json(data)}"
            
        except Exception as e:
            return f"Error getting ticket {ticket_id}: {str(e)}"
    
    async def create_ticket(self, **kwargs) -> str:
        """Create a new support ticket.
        
        Args:
            **kwargs: Ticket creation parameters.
            
        Returns:
            JSON string of created ticket data.
        """
        try:
            subject: str = kwargs["subject"].strip()
            body: str = kwargs["body"].strip()
            customer_id: int = kwargs["customer_id"]

            if not subject:
                return "Error creating ticket: subject cannot be empty."
            if not body:
                return "Error creating ticket: body cannot be empty."

            customer = await self.api_client.get(f"customers/{customer_id}")
            if not isinstance(customer, dict):
                return (
                    f"Error creating ticket: unable to load customer {customer_id}."
                )

            customer_email: Optional[str] = customer.get("email")
            if not customer_email and customer.get("channels"):
                for channel in customer["channels"]:
                    if channel.get("type") == "email" and channel.get("address"):
                        customer_email = channel["address"]
                        break

            if not customer_email:
                return (
                    "Error creating ticket: customer does not have an email address on file."
                )

            customer_name: Optional[str] = customer.get("name")
            if not customer_name:
                firstname = customer.get("firstname", "").strip()
                lastname = customer.get("lastname", "").strip()
                combined = " ".join(part for part in [firstname, lastname] if part)
                customer_name = combined or customer_email

            support_email = (
                os.getenv("GORGIAS_INBOX_EMAIL")
                or os.getenv("GORGIAS_SUPPORT_EMAIL")
                or getattr(self.api_client.auth, "username", None)
            )

            if not support_email:
                return (
                    "Error creating ticket: support email destination is not configured."
                )

            message_payload = {
                "from_agent": False,
                "public": True,
                "subject": subject,
                "body_text": body,
                "channel": "email",
                "via": "email",
                "sender": {"id": customer_id},
                "source": {
                    "type": "email",
                    "from": {
                        "name": customer_name,
                        "address": customer_email,
                    },
                    "to": [
                        {
                            "name": "Support",
                            "address": support_email,
                        }
                    ],
                    "cc": [],
                    "bcc": [],
                },
            }

            ticket_data = {
                "subject": subject,
                "status": kwargs.get("status", "open"),
                "priority": kwargs.get("priority", "normal"),
                "channel": "email",
                "via": "api",
                "messages": [message_payload],
            }

            assignee_id = kwargs.get("assignee_id")
            if assignee_id is not None:
                # Gorgias API expects assignee_user as an object with id field
                ticket_data["assignee_user"] = {"id": assignee_id}

            tags = kwargs.get("tags")
            if tags:
                # Gorgias API expects tags as array of objects with name field
                ticket_data["tags"] = [{"name": tag} for tag in tags]

            data = await self.api_client.post("tickets", data=ticket_data)
            ticket_identifier = (
                data.get("id", "unknown") if isinstance(data, dict) else "unknown"
            )
            return f"Created ticket {ticket_identifier}:\n{self._format_json(data)}"

        except Exception as e:
            return f"Error creating ticket: {str(e)}"
    
    async def update_ticket(self, ticket_id: int, **kwargs) -> str:
        """Update an existing ticket.
        
        Args:
            ticket_id: ID of the ticket to update.
            **kwargs: Update parameters.
            
        Returns:
            JSON string of updated ticket data.
        """
        try:
            # Build update data
            update_data = {}
            if "status" in kwargs:
                update_data["status"] = kwargs["status"]
            if "priority" in kwargs:
                update_data["priority"] = kwargs["priority"]
            if "assignee_id" in kwargs:
                # Gorgias API expects assignee_user as an object with id field
                update_data["assignee_user"] = {"id": kwargs["assignee_id"]}
            if "subject" in kwargs:
                update_data["subject"] = kwargs["subject"]
            
            data = await self.api_client.put(f"tickets/{ticket_id}", data=update_data)
            return f"Updated ticket {ticket_id}:\n{self._format_json(data)}"
            
        except Exception as e:
            return f"Error updating ticket {ticket_id}: {str(e)}"
    
    async def search_tickets(self, query: str, limit: int = 50) -> str:
        """Search tickets by content or other criteria.
        
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
            
            data = await self.api_client.get("tickets/search", params=params)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return (
                f"Found {count} tickets matching '{query}':\n"
                f"{self._format_json(data)}"
            )
            
        except Exception as e:
            return f"Error searching tickets: {str(e)}"
