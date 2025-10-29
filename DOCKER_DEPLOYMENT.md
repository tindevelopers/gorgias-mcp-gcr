# Docker Deployment Guide for Gorgias MCP Server

## 🐳 **Docker Solution Overview**

This Docker setup provides **two deployment modes**:

1. **MCP stdio mode** - For local development and VPS deployment
2. **HTTP mode** - For Railway deployment (healthchecks only)

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

### **Railway Deployment (HTTP mode)**
```bash
# Build and run in HTTP mode
docker-compose up gorgias-http-server

# Or run directly
docker run -p 3000:3000 \
  -e GORGIAS_API_KEY="your_api_key" \
  -e GORGIAS_USERNAME="your_email" \
  -e GORGIAS_BASE_URL="https://your-store.gorgias.com/api/" \
  -e RAILWAY_ENVIRONMENT=production \
  gorgias-mcp-server
```

## 🔧 **Docker Features**

### **Multi-Mode Support**
- **MCP stdio mode**: Full MCP functionality for external clients
- **HTTP mode**: Railway-compatible with healthcheck endpoints

### **Environment Detection**
- Automatically detects Railway environment
- Switches between MCP and HTTP modes accordingly

### **Security**
- Non-root user execution
- Minimal base image (python:3.13-slim)
- No unnecessary packages

## 📋 **Railway Deployment Steps**

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Docker support for Railway deployment"
   git push origin railway-deploy
   ```

2. **Railway will automatically**:
   - Detect Dockerfile
   - Build Docker image
   - Deploy with HTTP mode
   - Provide healthcheck endpoints

3. **Set environment variables** in Railway:
   - `GORGIAS_API_KEY`
   - `GORGIAS_USERNAME`
   - `GORGIAS_BASE_URL`
   - `DEBUG=false`

## 🌐 **Available Endpoints (Railway)**

- **`/`** - Health check
- **`/health`** - Detailed health status
- **`/status`** - Service information

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

### **Option 1: Railway (HTTP only)**
- ✅ Health checks work
- ✅ Status monitoring
- ❌ No MCP stdio support
- ❌ External clients can't connect

### **Option 2: Local Docker (MCP stdio)**
- ✅ Full MCP functionality
- ✅ External client support
- ✅ All 11 tools available
- ❌ Requires local machine

### **Option 3: VPS with Docker (Recommended)**
- ✅ Full MCP functionality
- ✅ External client support
- ✅ Always available
- ✅ Production ready

## 🚀 **Production Deployment**

For production MCP server deployment:

1. **Deploy to VPS**:
   ```bash
   # On your VPS
   git clone https://github.com/tindevelopers/gorgias-mcp-server.git
   cd gorgias-mcp-server
   docker-compose up -d gorgias-mcp-server
   ```

2. **Configure MCP clients** to connect to your VPS

3. **Use Railway** for monitoring and health checks only

## 📊 **Summary**

| Feature | Railway | Local Docker | VPS Docker |
|---------|---------|--------------|------------|
| MCP stdio | ❌ | ✅ | ✅ |
| HTTP healthcheck | ✅ | ✅ | ✅ |
| External clients | ❌ | ✅ | ✅ |
| Always available | ✅ | ❌ | ✅ |
| Production ready | ❌ | ❌ | ✅ |

**Recommendation**: Use **VPS with Docker** for production MCP server, and **Railway** for monitoring.
