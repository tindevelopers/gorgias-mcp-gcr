# Google Cloud Run Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the Gorgias MCP Server to Google Cloud Run with streaming support.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed (`gcloud` CLI)
3. **Docker** installed (for local testing)
4. **Project ID** in Google Cloud

## 📋 Setup Steps

### Step 1: Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### Step 2: Authenticate and Set Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 3: Configure Environment Variables

Set environment variables in Cloud Run:

```bash
gcloud run services update gorgias-mcp-server \
  --set-env-vars="GORGIAS_API_KEY=your_api_key,GORGIAS_USERNAME=your_email,GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/,DEBUG=false" \
  --region=us-central1
```

Or set them during initial deployment (see Step 4).

### Step 4: Deploy to Cloud Run

#### Option A: Using Cloud Build (Recommended)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# This will:
# 1. Build the Docker image
# 2. Push to Container Registry
# 3. Deploy to Cloud Run
```

#### Option B: Manual Deployment

```bash
# Build Docker image locally
docker build -f Dockerfile.cloudrun -t gcr.io/YOUR_PROJECT_ID/gorgias-mcp-server .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/gorgias-mcp-server

# Deploy to Cloud Run
gcloud run deploy gorgias-mcp-server \
  --image gcr.io/YOUR_PROJECT_ID/gorgias-mcp-server \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --port 8080 \
  --set-env-vars="GORGIAS_API_KEY=your_api_key,GORGIAS_USERNAME=your_email,GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/,DEBUG=false"
```

## 🔧 Configuration Options

### Always-On (Minimum Instances)

To ensure fast response times with no cold starts:

```bash
gcloud run services update gorgias-mcp-server \
  --min-instances 1 \
  --region us-central1
```

**Cost**: ~$72/month for 1 always-on instance

### Auto-Scaling

```bash
gcloud run services update gorgias-mcp-server \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1
```

### Memory and CPU

```bash
gcloud run services update gorgias-mcp-server \
  --memory 1Gi \
  --cpu 2 \
  --region us-central1
```

## 🌊 Streaming Support

The server supports streaming responses via Server-Sent Events (SSE).

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

### Streaming Request

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

The streaming response will use Server-Sent Events (SSE) format.

## 🔍 Testing

### Health Check

```bash
curl https://YOUR_SERVICE_URL.run.app/health
```

### List Tools

```bash
curl -X POST https://YOUR_SERVICE_URL.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

## 📊 Monitoring

### View Logs

```bash
gcloud run services logs read gorgias-mcp-server --region us-central1
```

### View Metrics

Visit Cloud Run console:
- https://console.cloud.google.com/run

### Set Up Alerts

1. Go to Cloud Monitoring
2. Create alerting policy
3. Monitor:
   - Request latency
   - Error rate
   - Instance count

## 🔄 Updates

### Update Code

```bash
# Make changes to code
git add .
git commit -m "Update MCP server"

# Deploy update
gcloud builds submit --config cloudbuild.yaml
```

### Update Environment Variables

```bash
gcloud run services update gorgias-mcp-server \
  --update-env-vars="DEBUG=true" \
  --region us-central1
```

## 🌍 Multi-Region Deployment

For lower latency, deploy to multiple regions:

```bash
# Deploy to US Central
gcloud run deploy gorgias-mcp-server-us \
  --image gcr.io/YOUR_PROJECT_ID/gorgias-mcp-server \
  --region us-central1

# Deploy to US East
gcloud run deploy gorgias-mcp-server-eu \
  --image gcr.io/YOUR_PROJECT_ID/gorgias-mcp-server \
  --region us-east1

# Use Cloud Load Balancer to route traffic
```

## 💰 Cost Optimization

### Scale to Zero (Not Recommended for AI)

```bash
gcloud run services update gorgias-mcp-server \
  --min-instances 0 \
  --region us-central1
```

**Warning**: This will cause cold starts (1-5 seconds) on first request.

### Right-Sizing

- **Memory**: Start with 512Mi, increase if needed
- **CPU**: 1 vCPU is usually sufficient
- **Instances**: 1 min for always-on, scale up based on traffic

## 🔐 Security

### Authentication (Optional)

To require authentication:

```bash
gcloud run services update gorgias-mcp-server \
  --no-allow-unauthenticated \
  --region us-central1
```

Then use service account or API key for requests.

### Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service gorgias-mcp-server \
  --domain mcp.yourdomain.com \
  --region us-central1
```

## 🐛 Troubleshooting

### Check Service Status

```bash
gcloud run services describe gorgias-mcp-server --region us-central1
```

### View Recent Logs

```bash
gcloud run services logs read gorgias-mcp-server --region us-central1 --limit 50
```

### Test Locally

```bash
# Build locally
docker build -f Dockerfile.cloudrun -t gorgias-mcp-server .

# Run locally
docker run -p 8080:8080 \
  -e GORGIAS_API_KEY=your_key \
  -e GORGIAS_USERNAME=your_email \
  -e GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/ \
  gorgias-mcp-server

# Test
curl http://localhost:8080/health
```

## 📝 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GORGIAS_API_KEY` | ✅ Yes | Your Gorgias API key | `a9030dea3e...` |
| `GORGIAS_USERNAME` | ✅ Yes | Your Gorgias email | `ai-developer@tin.info` |
| `GORGIAS_BASE_URL` | ✅ Yes | Gorgias API URL | `https://petstoredirect.gorgias.com/api/` |
| `DEBUG` | ❌ No | Enable debug logging | `false` |
| `PORT` | ❌ No | Server port (set by Cloud Run) | `8080` |

## 🎯 Best Practices

1. **Always-On**: Set `min-instances: 1` for fast AI responses
2. **Monitoring**: Set up alerts for errors and latency
3. **Logging**: Use structured logging for better debugging
4. **Scaling**: Monitor traffic and adjust max-instances
5. **Security**: Use environment variables, never commit secrets

## 🚀 Next Steps

1. Deploy to Cloud Run
2. Test the MCP endpoint
3. Configure Retell AI to use the Cloud Run URL
4. Monitor performance and costs
5. Optimize based on usage patterns

Your Gorgias MCP Server is now ready for production on Google Cloud Run! 🎉

