# Gorgias MCP Server

A Model Context Protocol (MCP) server for integrating with the Gorgias customer support platform. This server provides tools for managing customers, orders, and support tickets through the Gorgias API.

## Features

### Customer Management
- List customers with filtering options
- Get customer details by ID
- Create new customers
- Update existing customers
- Search customers by email, name, or other criteria
- Get all tickets for a specific customer

### Order Management
- List orders with filtering options
- Get order details by ID
- Search orders by customer, order number, or other criteria
- Get all orders for a specific customer
- Get order statistics and metrics

### Ticket Management
- List tickets with filtering by status, priority, assignee, or customer
- Get ticket details by ID
- Create new support tickets
- Update existing tickets (status, priority, assignee, subject)
- Search tickets by content or other criteria

## Quick Start

### Option 1: Automatic Setup (Recommended)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the setup script:**
```bash
python setup.py
```
The setup script will:
- Prompt you for your Gorgias credentials
- Validate the credentials
- Test the API connection
- Create a `.env` file with your configuration

3. **Start the MCP server:**
```bash
python -m src.server
```

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure credentials:**
```bash
# Copy the example file
cp env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

3. **Set environment variables:**
```bash
export GORGIAS_API_KEY="your_api_key_here"
export GORGIAS_USERNAME="your_email@example.com"
export GORGIAS_BASE_URL="https://your-store.gorgias.com/api/"
```

4. **Start the MCP server:**
```bash
python -m src.server
```

## MCP Inspector Setup

Add the server to your MCP configuration file:

```json
{
  "mcpServers": {
    "gorgias": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/gorgias-mcp-server",
      "env": {
        "GORGIAS_API_KEY": "${GORGIAS_API_KEY}",
        "GORGIAS_USERNAME": "${GORGIAS_USERNAME}",
        "GORGIAS_BASE_URL": "${GORGIAS_BASE_URL}"
      }
    }
  }
}
```

Then run MCP Inspector:
```bash
mcp-inspector
```

## Usage

Once configured, the MCP server will provide the following tools:

### Customer Tools
- `list_customers` - List all customers with optional filtering
- `get_customer` - Get details of a specific customer
- `create_customer` - Create a new customer
- `update_customer` - Update an existing customer
- `search_customers` - Search customers by email, name, or other criteria
- `get_customer_tickets` - Get all tickets for a specific customer

### Order Tools
- `list_orders` - List all orders with optional filtering
- `get_order` - Get details of a specific order
- `search_orders` - Search orders by customer, order number, or other criteria
- `get_customer_orders` - Get all orders for a specific customer
- `get_order_metrics` - Get order statistics and metrics

### Ticket Tools
- `list_tickets` - List all tickets with optional filtering
- `get_ticket` - Get details of a specific ticket
- `create_ticket` - Create a new support ticket
- `update_ticket` - Update an existing ticket
- `search_tickets` - Search tickets by content or other criteria

## Configuration

The server uses the following environment variables:

- `GORGIAS_API_KEY` (required): Your Gorgias API key
- `GORGIAS_BASE_URL` (optional): Your Gorgias API base URL (defaults to the example URL)

## API Client Features

The included API client provides:
- Automatic authentication with Bearer token
- Request timeout handling
- Error handling and logging
- Pagination support for large datasets
- Support for GET, POST, PUT, and DELETE operations

## Error Handling

All tools include comprehensive error handling and will return descriptive error messages if something goes wrong. Common error scenarios include:
- Invalid API credentials
- Network connectivity issues
- Invalid parameters
- API rate limiting
- Resource not found errors

## Development

To run the server in development mode:

```bash
python -m src.server
```

The server will start and listen for MCP protocol messages on stdin/stdout.

## License

This project is licensed under the MIT License.


