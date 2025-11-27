# Deploy to Pet Store Direct - Google Cloud Run

## ✅ Setup Complete

The Google Cloud project **"Pet Store Direct"** has been created with:
- Project ID: `pet-store-direct`
- Billing account linked
- Required APIs enabled:
  - Cloud Build API
  - Cloud Run API
  - Container Registry API

## 🚀 Deployment Options

### Option 1: Deploy via Google Cloud Console (Recommended if CLI has permission issues)

1. **Go to Cloud Build Console:**
   ```
   https://console.cloud.google.com/cloud-build/builds?project=pet-store-direct
   ```

2. **Click "Trigger" or "Run" and select:**
   - Source: Cloud Source Repositories or GitHub
   - Configuration: `cloudbuild.yaml`
   - Or upload the `cloudbuild.yaml` file

3. **After build completes, set environment variables:**
   ```bash
   gcloud run services update gorgias-mcp-server \
     --region=us-central1 \
     --set-env-vars="GORGIAS_API_KEY=your_api_key,GORGIAS_USERNAME=your_email,GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/,DEBUG=false"
   ```

### Option 2: Manual Deployment via Cloud Console

1. **Build container image:**
   - Go to: https://console.cloud.google.com/cloud-build/builds?project=pet-store-direct
   - Click "Create Build"
   - Connect to GitHub repository or upload source
   - Use `Dockerfile.cloudrun`

2. **Deploy to Cloud Run:**
   - Go to: https://console.cloud.google.com/run?project=pet-store-direct
   - Click "Create Service"
   - Select the container image
   - Configure:
     - Service name: `gorgias-mcp-server`
     - Region: `us-central1`
     - Allow unauthenticated: Yes
     - Min instances: 1
     - Max instances: 10
     - Memory: 512Mi
     - CPU: 1
     - Port: 8080
     - Timeout: 60s

3. **Set Environment Variables:**
   - GORGIAS_API_KEY: (your API key)
   - GORGIAS_USERNAME: (your email)
   - GORGIAS_BASE_URL: `https://petstoredirect.gorgias.com/api/`
   - DEBUG: `false`

### Option 3: Fix Permissions and Use CLI

If you encounter permission errors, you may need to:

1. **Check organization policies:**
   ```bash
   gcloud resource-manager org-policies list --project=pet-store-direct
   ```

2. **Grant yourself Cloud Build permissions:**
   ```bash
   gcloud projects add-iam-policy-binding pet-store-direct \
     --member="user:developer@tin.info" \
     --role="roles/cloudbuild.builds.editor"
   ```

3. **Try deployment again:**
   ```bash
   cd /Users/gene/Projects/gorgias-mcp-gcr
   gcloud builds submit --config cloudbuild.yaml
   ```

## 📋 Current Project Status

- **Project ID:** `pet-store-direct`
- **Project Number:** `880489367524`
- **Billing:** ✅ Linked (Account: 01E604-AA80D1-9D66C7)
- **APIs Enabled:** ✅ Cloud Build, Cloud Run, Container Registry
- **IAM Permissions:** ✅ Service accounts configured

## 🔧 Next Steps

1. **Get Gorgias Credentials:**
   - GORGIAS_API_KEY
   - GORGIAS_USERNAME (email)
   - GORGIAS_BASE_URL (default: https://petstoredirect.gorgias.com/api/)

2. **Deploy using one of the options above**

3. **Test the deployment:**
   ```bash
   # Get service URL
   SERVICE_URL=$(gcloud run services describe gorgias-mcp-server \
     --region=us-central1 \
     --format='value(status.url)')
   
   # Test health check
   curl $SERVICE_URL/health
   
   # Test MCP endpoint
   curl -X POST $SERVICE_URL/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/list",
       "params": {}
     }'
   ```

## 📊 Monitoring

- **View logs:**
  ```bash
  gcloud run services logs read gorgias-mcp-server --region=us-central1
  ```

- **View in console:**
  https://console.cloud.google.com/run/detail/us-central1/gorgias-mcp-server?project=pet-store-direct

## 🐛 Troubleshooting

If you encounter permission errors:
1. Check that billing is enabled (✅ Done)
2. Verify APIs are enabled (✅ Done)
3. Check organization policies that might block Cloud Build
4. Try deploying via Cloud Console instead


