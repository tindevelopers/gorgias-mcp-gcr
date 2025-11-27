# Setting Gorgias Credentials for Cloud Run

## Quick CLI Command

Replace `your_api_key_here` and `your_email@example.com` with your actual Gorgias credentials:

```bash
gcloud run services update gorgias-mcp-server \
  --region=us-central1 \
  --set-env-vars="GORGIAS_API_KEY=your_api_key_here,GORGIAS_USERNAME=your_email@example.com,GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/,DEBUG=false" \
  --project=pet-store-direct
```

## Example

```bash
gcloud run services update gorgias-mcp-server \
  --region=us-central1 \
  --set-env-vars="GORGIAS_API_KEY=abc123xyz789,GORGIAS_USERNAME=admin@petstoredirect.com,GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/,DEBUG=false" \
  --project=pet-store-direct
```

## Option 2: Interactive Script

Run the helper script which will prompt you for credentials:

```bash
./set-gorgias-credentials.sh
```

Or pass credentials as arguments:

```bash
./set-gorgias-credentials.sh "your_api_key" "your_email@example.com" "https://petstoredirect.gorgias.com/api/"
```

## Verify Credentials

After setting credentials, verify they're configured:

```bash
gcloud run services describe gorgias-mcp-server \
  --region=us-central1 \
  --format="table(spec.template.spec.containers[0].env)"
```

## Test the Service

After updating credentials, test the health endpoint:

```bash
SERVICE_URL=$(gcloud run services describe gorgias-mcp-server \
  --region=us-central1 \
  --format='value(status.url)')

curl $SERVICE_URL/health
```

## Notes

- The service will automatically restart with the new credentials
- Changes take effect immediately (no downtime)
- Credentials are stored securely in Cloud Run
- The `GORGIAS_BASE_URL` defaults to `https://petstoredirect.gorgias.com/api/` if not specified


