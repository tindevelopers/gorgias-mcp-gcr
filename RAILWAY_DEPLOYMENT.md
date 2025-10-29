# Railway Deployment Guide for Gorgias MCP Server

This guide will help you deploy the Gorgias MCP Server to Railway.

## 🚀 Quick Deployment (Recommended)

### Method 1: GitHub Integration (Easiest)

1. **Connect to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Sign in with your GitHub account
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `tindevelopers/gorgias-mcp-server`
   - Select the `railway-deploy` branch

2. **Configure Environment Variables:**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add these required variables:
     ```
     GORGIAS_API_KEY=your_actual_api_key_here
     GORGIAS_USERNAME=your_email@example.com
     GORGIAS_BASE_URL=https://your-store.gorgias.com/api/
     DEBUG=false
     ```

3. **Deploy:**
   - Railway will automatically detect the Python project
   - It will use the `railway.json` configuration
   - The server will start using `python start.py`

### Method 2: Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Deploy from local directory:**
   ```bash
   cd /Users/foo/projects/gorgias-mcp-server
   railway up
   ```

4. **Set environment variables:**
   ```bash
   railway variables set GORGIAS_API_KEY=your_actual_api_key_here
   railway variables set GORGIAS_USERNAME=your_email@example.com
   railway variables set GORGIAS_BASE_URL=https://your-store.gorgias.com/api/
   ```

## 📋 Configuration Files

The following files are configured for Railway deployment:

- `railway.json` - Railway deployment configuration
- `Procfile` - Process file for web dyno
- `runtime.txt` - Python version specification
- `start.py` - Railway-optimized startup script
- `requirements.txt` - Python dependencies

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GORGIAS_API_KEY` | ✅ Yes | Your Gorgias API key | `95e612f885f4ce9b880f8ff2086e2ca3a569c48cbc8657ce990feaf17f45bd44` |
| `GORGIAS_USERNAME` | ✅ Yes | Your Gorgias email | `gene@tin.info` |
| `GORGIAS_BASE_URL` | ✅ Yes | Your Gorgias API URL | `https://petstoredirect.gorgias.com/api/` |
| `DEBUG` | ❌ No | Enable debug logging | `false` |

## 🏥 Health Checks

Railway will perform health checks on your MCP server:
- **Path**: `/` (root endpoint)
- **Timeout**: 100 seconds
- **Restart Policy**: On failure (max 10 retries)

## 📊 Monitoring

After deployment, you can monitor your MCP server:
- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Monitor CPU, memory, and network usage
- **Health**: Check server health status

## 🔄 Updates

To update your deployment:
1. Push changes to the `railway-deploy` branch
2. Railway will automatically redeploy
3. Or manually trigger redeploy from Railway dashboard

## 🛠️ Troubleshooting

### Common Issues:

1. **Environment Variables Not Set:**
   - Check Railway Variables tab
   - Ensure all required variables are set

2. **Build Failures:**
   - Check Railway build logs
   - Verify `requirements.txt` is correct

3. **Server Won't Start:**
   - Check Railway deployment logs
   - Verify environment variables are correct

4. **MCP Connection Issues:**
   - Ensure your Gorgias credentials are valid
   - Check that the API URL is correct

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test locally with `python start.py`
4. Check Gorgias API connectivity

## 🎯 Next Steps After Deployment

1. **Test the MCP Server:**
   - Use MCP Inspector to test the connection
   - Verify all tools are working correctly

2. **Configure MCP Client:**
   - Update your MCP client configuration
   - Point to your Railway deployment URL

3. **Monitor Performance:**
   - Set up Railway monitoring
   - Monitor API usage and performance

Your Gorgias MCP Server is now ready for production use on Railway! 🎉
