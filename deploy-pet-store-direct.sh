#!/bin/bash
# Deploy Gorgias MCP Server to Google Cloud Run - Pet Store Direct Project

set -e

PROJECT_ID="pet-store-direct"
REGION="us-central1"
SERVICE_NAME="gorgias-mcp-server"

echo "🚀 Deploying Gorgias MCP Server to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Check if billing is enabled
echo "🔍 Checking billing status..."
BILLING_ENABLED=$(gcloud beta billing projects describe $PROJECT_ID --format="value(billingEnabled)" 2>&1 || echo "false")

if [ "$BILLING_ENABLED" != "True" ]; then
    echo "⚠️  Billing is not enabled for this project."
    echo ""
    echo "To enable billing:"
    echo "1. Go to: https://console.cloud.google.com/billing"
    echo "2. Link a billing account to project: $PROJECT_ID"
    echo "3. Or run: gcloud beta billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com 2>&1 || {
    echo "❌ Failed to enable APIs. Please ensure billing is enabled."
    exit 1
}

# Check for environment variables
echo ""
echo "📝 Environment Variables Configuration"
echo "The following environment variables are required:"
echo "  - GORGIAS_API_KEY"
echo "  - GORGIAS_USERNAME"
echo "  - GORGIAS_BASE_URL (default: https://petstoredirect.gorgias.com/api/)"
echo ""

# Prompt for environment variables if not set
if [ -z "$GORGIAS_API_KEY" ]; then
    read -p "Enter GORGIAS_API_KEY: " GORGIAS_API_KEY
fi

if [ -z "$GORGIAS_USERNAME" ]; then
    read -p "Enter GORGIAS_USERNAME (email): " GORGIAS_USERNAME
fi

if [ -z "$GORGIAS_BASE_URL" ]; then
    GORGIAS_BASE_URL="https://petstoredirect.gorgias.com/api/"
    echo "Using default GORGIAS_BASE_URL: $GORGIAS_BASE_URL"
fi

# Build and deploy
echo ""
echo "🔨 Building and deploying..."
echo "This may take several minutes..."
echo ""

gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_GORGIAS_API_KEY="$GORGIAS_API_KEY",_GORGIAS_USERNAME="$GORGIAS_USERNAME",_GORGIAS_BASE_URL="$GORGIAS_BASE_URL" 2>&1 || {
    echo "❌ Build/deployment failed"
    exit 1
}

# Set environment variables after deployment
echo ""
echo "🔧 Setting environment variables..."
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="GORGIAS_API_KEY=$GORGIAS_API_KEY,GORGIAS_USERNAME=$GORGIAS_USERNAME,GORGIAS_BASE_URL=$GORGIAS_BASE_URL,DEBUG=false" 2>&1 || {
    echo "⚠️  Failed to set environment variables. You may need to set them manually."
}

# Get service URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📡 Service URL:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' 2>&1)
echo "$SERVICE_URL"
echo ""
echo "🧪 Test health check:"
echo "curl $SERVICE_URL/health"
echo ""
echo "🔧 MCP endpoint:"
echo "curl -X POST $SERVICE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"
echo ""
echo "📊 View logs:"
echo "gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo ""
echo "🎉 Deployment successful!"


