#!/bin/bash
# Set Gorgias credentials for Cloud Run service

set -e

PROJECT_ID="pet-store-direct"
REGION="us-central1"
SERVICE_NAME="gorgias-mcp-server"

echo "🔧 Setting Gorgias credentials for Cloud Run service"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo ""

# Check if credentials are provided as arguments
if [ $# -ge 2 ]; then
    GORGIAS_API_KEY=$1
    GORGIAS_USERNAME=$2
    GORGIAS_BASE_URL=${3:-"https://petstoredirect.gorgias.com/api/"}
else
    # Prompt for credentials
    read -p "Enter GORGIAS_API_KEY: " GORGIAS_API_KEY
    read -p "Enter GORGIAS_USERNAME (email): " GORGIAS_USERNAME
    read -p "Enter GORGIAS_BASE_URL [https://petstoredirect.gorgias.com/api/]: " GORGIAS_BASE_URL
    GORGIAS_BASE_URL=${GORGIAS_BASE_URL:-"https://petstoredirect.gorgias.com/api/"}
fi

echo ""
echo "Updating environment variables..."

gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="GORGIAS_API_KEY=$GORGIAS_API_KEY,GORGIAS_USERNAME=$GORGIAS_USERNAME,GORGIAS_BASE_URL=$GORGIAS_BASE_URL,DEBUG=false" \
    --project=$PROJECT_ID 2>&1

echo ""
echo "✅ Credentials updated!"
echo ""
echo "Service URL:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)' 2>&1)
echo "$SERVICE_URL"
echo ""
echo "🧪 Test health check:"
echo "curl $SERVICE_URL/health"
echo ""
echo "🔧 Test MCP endpoint:"
echo "curl -X POST $SERVICE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"


