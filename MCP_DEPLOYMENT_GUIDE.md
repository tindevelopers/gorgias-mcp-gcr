# MCP Server Deployment Guide

## ✅ **Google Cloud Run Deployment (Recommended)**

This server is designed for **Google Cloud Run** deployment with **HTTPS streaming support**:
- ✅ **HTTP/HTTPS** - Full HTTP-based MCP protocol support
- ✅ **Streaming** - Server-Sent Events (SSE) for real-time responses
- ✅ **HTTPS** - Secure connections via Cloud Run's managed HTTPS
- ✅ **Scalable** - Auto-scaling with Cloud Run
- ✅ **Production-ready** - Always-on instances for fast responses

## 🚀 **Deployment Options**

### Option 1: Google Cloud Run (Production - Recommended)

Deploy to Google Cloud Run for production use with HTTPS streaming:

```bash
# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or see CLOUD_RUN_DEPLOYMENT.md for detailed instructions
```

**Features:**
- HTTPS endpoint: `https://your-service.run.app/mcp`
- Streaming support via Server-Sent Events (SSE)
- Auto-scaling
- Always-on instances (configurable)
- Managed HTTPS certificates

### Option 2: Local Development (MCP stdio)

For local development and testing with MCP Inspector:

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server locally
python -m src.server
```

### Option 3: Docker with stdio support

For local Docker testing:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "src.server"]
```

## 🔧 **MCP Client Configuration**

### For Google Cloud Run (HTTPS)

Use HTTP-based MCP protocol over HTTPS:

```json
{
  "mcpServers": {
    "gorgias": {
      "url": "https://your-service.run.app/mcp",
      "transport": "http",
      "streaming": true
    }
  }
}
```

### For Local Development (stdio)

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

## 🌊 **HTTPS Streaming Support**

The Google Cloud Run deployment supports **Server-Sent Events (SSE)** for streaming responses:

### Standard Request (Non-Streaming)

```bash
curl -X POST https://YOUR_SERVICE_URL.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_ticket",
      "arguments": {"ticket_id": 63168463}
    }
  }'
```

### Streaming Request (HTTPS SSE)

```bash
curl -X POST https://YOUR_SERVICE_URL.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_ticket",
      "arguments": {"ticket_id": 63168463},
      "stream": true
    }
  }'
```

The streaming response uses Server-Sent Events (SSE) format over HTTPS.

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

## 🎯 **Recommendation**

For production deployment:
1. **Use Google Cloud Run** - HTTPS streaming support, auto-scaling, production-ready
2. **Configure always-on instances** - For fast response times
3. **Set up monitoring** - Use Cloud Run metrics and logs
4. **Use HTTPS endpoint** - Secure connections via Cloud Run's managed certificates

See `CLOUD_RUN_DEPLOYMENT.md` for detailed deployment instructions.
