"""Customer management tools for Gorgias MCP server."""

import json
from typing import Any, Dict, List, Optional, Tuple
from mcp.types import Tool
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
    
    def _format_json(self, data: Any) -> str:
        """Format data as a pretty-printed JSON string."""
        try:
            return json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError):
            return str(data)

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
            
            data = await self.api_client.get("customers", params=params)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return f"Found {count} customers:\n{self._format_json(data)}"
            
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
            data = await self.api_client.get(f"customers/{customer_id}")
            return f"Customer {customer_id} details:\n{self._format_json(data)}"
            
        except Exception as e:
            return f"Error getting customer {customer_id}: {str(e)}"
    
    async def create_customer(self, **kwargs) -> str:
        """Create a new customer, appending extra fields when possible.

        This method follows the workflow requested by the user:

        * Check if a customer already exists using email/phone identifiers.
        * If the customer exists, append/update the record with any extra data.
        * If the customer does not exist, create the minimal viable record and
          then append the additional details.

        Args:
            **kwargs: Customer creation parameters.

        Returns:
            A formatted string describing the actions taken.
        """

        try:
            email: Optional[str] = kwargs.get("email")
            phone: Optional[str] = kwargs.get("phone")

            if not email and not phone:
                return "Error creating customer: either email or phone must be provided"

            messages: List[str] = []

            existing = await self._find_existing_customer(email=email, phone=phone)

            # Extract additional data to append after ensuring the record exists
            update_payload, channel_payload = self._build_update_payload(kwargs)

            if update_payload.get("email") == email and len(update_payload) == 1:
                update_payload.pop("email")

            if existing:
                customer_id = existing.get("id")
                messages.append(
                    f"Customer already exists (ID: {customer_id}). Skipping creation."
                )

                update_messages = await self._append_customer_data(
                    customer_id,
                    update_payload,
                    channel_payload,
                )
                messages.extend(update_messages)
            else:
                create_payload = self._build_minimal_create_payload(email=email, phone=phone)
                created = await self.api_client.post("customers", data=create_payload)
                customer_id = created.get("id", "unknown") if isinstance(created, dict) else "unknown"
                messages.append(
                    f"Created customer {customer_id}:\n{self._format_json(created)}"
                )

                update_messages = await self._append_customer_data(
                    customer_id,
                    update_payload,
                    channel_payload,
                )
                messages.extend(update_messages)

            return "\n".join(messages)

        except Exception as e:
            return f"Error creating customer: {str(e)}"

    async def _append_customer_data(
        self,
        customer_id: Any,
        update_payload: Dict[str, Any],
        channel_payload: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Append additional details to an existing customer record."""

        messages: List[str] = []

        # Get existing customer data to preserve channels
        existing = await self._get_customer_details(customer_id)
        if existing is None:
            messages.append(
                f"Warning: Unable to retrieve customer {customer_id}; skipping update."
            )
            return messages

        # Build the complete update payload
        base_payload = self._build_base_update_payload(existing)
        merged_payload = {**base_payload, **update_payload}

        # Handle channels properly - preserve existing channels and add/update phone
        channels = []
        
        # Preserve existing channels (except phone if we're updating it)
        phone_updated = False
        for channel in existing.get("channels", []):
            if channel.get("type") == "phone" and channel_payload:
                # Skip old phone channel if we're updating phone
                phone_updated = True
                continue
            elif channel.get("type") == "email" or not channel_payload:
                # Keep email channels and other non-phone channels
                channels.append(channel)

        # Add new phone channel if provided
        if channel_payload:
            channels.append(channel_payload)
        elif not phone_updated:
            # If no phone update requested, keep existing phone channels
            for channel in existing.get("channels", []):
                if channel.get("type") == "phone":
                    channels.append(channel)

        # Include channels in the update payload
        if channels:
            merged_payload["channels"] = channels

        if not merged_payload:
            messages.append(
                f"Skipped updating customer {customer_id}: no valid data to send."
            )
        else:
            try:
                updated = await self.api_client.put(
                    f"customers/{customer_id}",
                    data=merged_payload,
                )
                messages.append(
                    f"Updated customer {customer_id}:\n{self._format_json(updated)}"
                )
            except Exception as update_error:
                messages.append(
                    f"Warning: Failed to update customer {customer_id}: {update_error}"
                )

        if not messages:
            messages.append(f"No additional data provided to append for customer {customer_id}.")

        return messages

    async def _find_existing_customer(
        self,
        *,
        email: Optional[str],
        phone: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Search for an existing customer by email or phone."""

        # Prefer email lookup because it is deterministic
        if email:
            try:
                response = await self.api_client.get(
                    "customers",
                    params={"email": email, "limit": 1}
                )
                data = response.get("data") if isinstance(response, dict) else None
                if data:
                    return data[0]
            except Exception:
                pass

        # Fall back to generic search when only phone is provided
        if phone:
            try:
                response = await self.api_client.get(
                    "customers/search",
                    params={"q": phone, "limit": 1}
                )
                data = response.get("data") if isinstance(response, dict) else None
                if data:
                    return data[0]
            except Exception:
                pass

        return None

    def _build_minimal_create_payload(
        self,
        *,
        email: Optional[str],
        phone: Optional[str]
    ) -> Dict[str, Any]:
        """Create the minimal payload required to create a customer."""

        payload: Dict[str, Any] = {}

        if email:
            payload["email"] = email

        # If no email is provided, attempt to create using a phone channel
        if phone and not email:
            payload["channels"] = [
                {
                    "type": "phone",
                    "address": phone,
                    "preferred": True,
                }
            ]

        return payload

    def _build_update_payload(
        self,
        kwargs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Prepare payloads for updating customer core fields and channels."""

        update_payload: Dict[str, Any] = {}
        channel_payload: Optional[Dict[str, Any]] = None

        field_mapping = {
            "first_name": "firstname",
            "last_name": "lastname",
            "name": "name",
            "language": "language",
            "email": "email",
        }

        for source, target in field_mapping.items():
            value = kwargs.get(source)
            if isinstance(value, str):
                value = value.strip()
            if value:
                update_payload[target] = value

        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        explicit_name = kwargs.get("name")

        if isinstance(first_name, str):
            first_name = first_name.strip()
        if isinstance(last_name, str):
            last_name = last_name.strip()
        if isinstance(explicit_name, str):
            explicit_name = explicit_name.strip()

        if explicit_name:
            update_payload["name"] = explicit_name
        else:
            parts = [part for part in (first_name, last_name) if part]
            if parts:
                update_payload["name"] = " ".join(parts)

        phone = kwargs.get("phone")
        if phone:
            channel_payload = {
                "type": "phone",
                "address": phone,
                "preferred": True,
            }

        return update_payload, channel_payload

    async def _get_customer_details(self, customer_id: Any) -> Optional[Dict[str, Any]]:
        """Retrieve the latest customer details to support update operations."""

        try:
            data = await self.api_client.get(f"customers/{customer_id}")
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def _build_base_update_payload(
        self,
        existing: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare required base fields for a customer update request."""

        if not existing:
            return {}

        base_fields: Dict[str, Any] = {}

        for key in ["email", "name", "language", "firstname", "lastname"]:
            value = existing.get(key)
            if value:
                base_fields[key] = value

        if not base_fields.get("email") and existing.get("channels"):
            for channel in existing["channels"]:
                if channel.get("type") == "email" and channel.get("address"):
                    base_fields["email"] = channel["address"]
                    break

        return base_fields
    
    async def update_customer(self, customer_id: int, **kwargs) -> str:
        """Update an existing customer.
        
        Args:
            customer_id: ID of the customer to update.
            **kwargs: Update parameters.
            
        Returns:
            JSON string of updated customer data.
        """
        try:
            update_payload, channel_payload = self._build_update_payload(kwargs)

            if not update_payload and not channel_payload:
                return f"No valid update fields provided for customer {customer_id}."

            messages = await self._append_customer_data(
                customer_id,
                update_payload,
                channel_payload,
            )

            return "\n".join(messages)
            
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
            
            data = await self.api_client.get("customers/search", params=params)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return (
                f"Found {count} customers matching '{query}':\n"
                f"{self._format_json(data)}"
            )
            
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
            
            data = await self.api_client.get("tickets", params=params)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return (
                f"Found {count} tickets for customer {customer_id}:\n"
                f"{self._format_json(data)}"
            )
            
        except Exception as e:
            return f"Error getting tickets for customer {customer_id}: {str(e)}"


