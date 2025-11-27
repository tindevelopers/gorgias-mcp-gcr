# Docker Deployment Guide for Gorgias MCP Server

## 🐳 **Docker Solution Overview**

This Docker setup provides **two deployment modes**:

1. **MCP stdio mode** - For local development and testing
2. **HTTP mode** - For Google Cloud Run deployment with HTTPS streaming support

## 🚀 **Quick Start**

### **Local Development (MCP stdio)**
```bash
# Build and run in MCP mode
docker-compose up gorgias-mcp-server

# Or run directly
docker build -t gorgias-mcp-server .
docker run -it --rm \
  -e GORGIAS_API_KEY="your_api_key" \
  -e GORGIAS_USERNAME="your_email" \
  -e GORGIAS_BASE_URL="https://your-store.gorgias.com/api/" \
  gorgias-mcp-server
```

### **Google Cloud Run Deployment (HTTP mode with streaming)**
```bash
# Build and run locally for testing
docker-compose up gorgias-cloud-run-server

# Or run directly
docker run -p 8080:8080 \
  -e GORGIAS_API_KEY="your_api_key" \
  -e GORGIAS_USERNAME="your_email" \
  -e GORGIAS_BASE_URL="https://your-store.gorgias.com/api/" \
  -e PORT=8080 \
  gorgias-mcp-server
```

## 🔧 **Docker Features**

### **Multi-Mode Support**
- **MCP stdio mode**: Full MCP functionality for local development
- **HTTP mode**: Google Cloud Run deployment with HTTPS streaming support

### **Environment Detection**
- Automatically detects PORT environment variable
- Switches between MCP stdio and HTTP modes accordingly

### **Security**
- Non-root user execution
- Minimal base image (python:3.13-slim)
- No unnecessary packages

## 📋 **Google Cloud Run Deployment Steps**

1. **Build and deploy using Cloud Build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

2. **Or deploy manually**:
   ```bash
   # Build Docker image
   docker build -f Dockerfile.cloudrun -t gcr.io/PROJECT_ID/gorgias-mcp-server .
   
   # Push to Container Registry
   docker push gcr.io/PROJECT_ID/gorgias-mcp-server
   
   # Deploy to Cloud Run
   gcloud run deploy gorgias-mcp-server \
     --image gcr.io/PROJECT_ID/gorgias-mcp-server \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated
   ```

3. **Set environment variables** in Cloud Run:
   - `GORGIAS_API_KEY`
   - `GORGIAS_USERNAME`
   - `GORGIAS_BASE_URL`
   - `DEBUG=false`

## 🌐 **Available Endpoints (Cloud Run)**

- **`/`** - Health check
- **`/health`** - Detailed health status with tools list
- **`/mcp`** - MCP protocol endpoint (POST)
  - Supports standard JSON-RPC requests
  - Supports streaming with `stream: true` parameter

## 🔧 **MCP Client Configuration**

For external MCP clients (like retellai.com), use **local Docker deployment**:

```json
{
  "mcpServers": {
    "gorgias": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "GORGIAS_API_KEY=your_api_key",
        "-e", "GORGIAS_USERNAME=your_email", 
        "-e", "GORGIAS_BASE_URL=https://your-store.gorgias.com/api/",
        "gorgias-mcp-server"
      ],
      "cwd": "/path/to/gorgias-mcp-server"
    }
  }
}
```

## 🎯 **Deployment Options**

### **Option 1: Google Cloud Run (Recommended)**
- ✅ HTTPS streaming support
- ✅ Server-Sent Events (SSE) for real-time responses
- ✅ Auto-scaling
- ✅ Always-on instances (configurable)
- ✅ Production-ready
- ✅ Managed HTTPS certificates
- ✅ Full MCP protocol over HTTP

### **Option 2: Local Docker (MCP stdio)**
- ✅ Full MCP stdio functionality
- ✅ External client support
- ✅ All tools available
- ❌ Requires local machine
- ❌ No HTTPS

## 🚀 **Production Deployment**

For production deployment, use **Google Cloud Run**:

1. **Deploy to Cloud Run**:
   ```bash
   # Use Cloud Build (recommended)
   gcloud builds submit --config cloudbuild.yaml
   
   # Or see CLOUD_RUN_DEPLOYMENT.md for detailed instructions
   ```

2. **Configure MCP clients** to use HTTPS endpoint:
   - Endpoint: `https://your-service.run.app/mcp`
   - Method: POST
   - Content-Type: application/json
   - Supports streaming with `stream: true` parameter

3. **Monitor via Cloud Run console**:
   - Logs, metrics, and health checks

## 📊 **Summary**

| Feature | Google Cloud Run | Local Docker |
|---------|------------------|--------------|
| HTTPS | ✅ | ❌ |
| Streaming (SSE) | ✅ | ❌ |
| MCP HTTP protocol | ✅ | ❌ |
| MCP stdio | ❌ | ✅ |
| Auto-scaling | ✅ | ❌ |
| Always available | ✅ | ❌ |
| Production ready | ✅ | ❌ |

**Recommendation**: Use **Google Cloud Run** for production deployment with HTTPS streaming support.
