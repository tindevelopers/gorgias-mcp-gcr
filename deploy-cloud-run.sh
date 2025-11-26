#!/bin/bash
# Quick deployment script for Google Cloud Run

set -e

PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="gorgias-mcp-server"

echo "🚀 Deploying Gorgias MCP Server to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Build and deploy
echo "🔨 Building and deploying..."
gcloud builds submit --config cloudbuild.yaml

echo "✅ Deployment complete!"
echo ""
echo "📡 Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
echo ""
echo "🧪 Test health check:"
echo "curl \$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')/health"

