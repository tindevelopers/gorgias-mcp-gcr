# MCP Server Deployment Guide

## 🚨 **Important: Railway Limitation**

**Railway is NOT suitable for MCP servers** because:
- MCP requires **stdio communication** (stdin/stdout)
- Railway is designed for **HTTP services**
- External MCP clients cannot connect to Railway-deployed stdio services

## ✅ **Proper MCP Deployment Options**

### Option 1: Local Development (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server locally
python -m src.server

# Or use the example
python example_usage.py
```

### Option 2: Docker with stdio support
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "src.server"]
```

### Option 3: VPS/Server with stdio
- Deploy to a VPS that supports stdio
- Use systemd to manage the service
- Ensure proper environment variables

## 🔧 **MCP Client Configuration**

For external MCP clients (like retellai.com), use this configuration:

```json
{
  "mcpServers": {
    "gorgias": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/gorgias-mcp-server",
      "env": {
        "GORGIAS_API_KEY": "your_api_key",
        "GORGIAS_USERNAME": "your_email",
        "GORGIAS_BASE_URL": "https://your-store.gorgias.com/api/"
      }
    }
  }
}
```

## 🚀 **Quick Start for External Clients**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tindevelopers/gorgias-mcp-server.git
   cd gorgias-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   export GORGIAS_API_KEY="your_api_key"
   export GORGIAS_USERNAME="your_email"
   export GORGIAS_BASE_URL="https://your-store.gorgias.com/api/"
   ```

4. **Test the server**:
   ```bash
   python -m src.server
   ```

5. **Configure your MCP client** with the stdio command

## 📋 **Available Tools**

The MCP server provides these tools:
- `list_customers` - List Gorgias customers
- `get_customer` - Get customer details
- `create_customer` - Create new customer
- `update_customer` - Update customer information
- `search_customers` - Search customers
- `get_customer_tickets` - Get customer's tickets
- `list_tickets` - List Gorgias tickets
- `get_ticket` - Get ticket details
- `create_ticket` - Create new ticket
- `update_ticket` - Update ticket information
- `search_tickets` - Search tickets

## ⚠️ **Why Railway Doesn't Work**

Railway is designed for:
- ✅ HTTP web services
- ✅ REST APIs
- ✅ Web applications

MCP requires:
- ❌ stdio communication (stdin/stdout)
- ❌ Process-based communication
- ❌ Direct process spawning

## 🎯 **Recommendation**

For production MCP server deployment:
1. **Use a VPS** (DigitalOcean, Linode, AWS EC2)
2. **Deploy with Docker** and stdio support
3. **Use systemd** for process management
4. **Configure proper networking** for MCP clients

The current Railway deployment is only useful for:
- Health checks
- Status monitoring
- Testing HTTP endpoints

But **NOT for actual MCP client connections**.
