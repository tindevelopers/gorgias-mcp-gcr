# Railway Multi-Environment Setup Guide

## 🏗️ Environment Strategy Overview

This guide sets up a disciplined **Develop → Staging → Production** workflow using Railway.

## 📋 Branch Strategy

```
main (production)          → Railway Production Environment
├── staging                → Railway Staging Environment  
└── develop                → Railway Development Environment
```

### Branch Purposes:

- **`main`**: Production-ready code, only merged from staging after thorough testing
- **`staging`**: Pre-production testing environment, merged from develop
- **`develop`**: Active development branch, feature branches merge here first

## 🚂 Railway Setup: Three Separate Projects

### Option 1: Separate Railway Projects (Recommended)

Create **three separate Railway projects**, one for each environment:

#### 1. **Production Project** (`gorgias-mcp-server-production`)
- **Git Branch**: `main`
- **Railway Project Name**: `gorgias-mcp-server-production`
- **URL**: `https://gorgias-mcp-server-production.up.railway.app`
- **Purpose**: Live production environment
- **Deployment**: Auto-deploy from `main` branch

#### 2. **Staging Project** (`gorgias-mcp-server-staging`)
- **Git Branch**: `staging`
- **Railway Project Name**: `gorgias-mcp-server-staging`
- **URL**: `https://gorgias-mcp-server-staging.up.railway.app`
- **Purpose**: Pre-production testing
- **Deployment**: Auto-deploy from `staging` branch

#### 3. **Development Project** (`gorgias-mcp-server-develop`)
- **Git Branch**: `develop`
- **Railway Project Name**: `gorgias-mcp-server-develop`
- **URL**: `https://gorgias-mcp-server-develop.up.railway.app`
- **Purpose**: Active development testing
- **Deployment**: Auto-deploy from `develop` branch

## 🔧 Setup Instructions

### Step 1: Create Branches

```bash
# Create develop branch from main
git checkout main
git checkout -b develop
git push origin develop

# Create staging branch from main
git checkout main
git checkout -b staging
git push origin staging
```

### Step 2: Create Railway Projects

#### Production Project:
1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose `tindevelopers/gorgias-mcp-server`
5. **Select branch**: `main`
6. **Project name**: `gorgias-mcp-server-production`

#### Staging Project:
1. Click **"New Project"** again
2. Select **"Deploy from GitHub repo"**
3. Choose `tindevelopers/gorgias-mcp-server`
4. **Select branch**: `staging`
5. **Project name**: `gorgias-mcp-server-staging`

#### Development Project:
1. Click **"New Project"** again
2. Select **"Deploy from GitHub repo"**
3. Choose `tindevelopers/gorgias-mcp-server`
4. **Select branch**: `develop`
5. **Project name**: `gorgias-mcp-server-develop`

### Step 3: Configure Environment Variables

#### Production Environment Variables:
```
GORGIAS_API_KEY=<production_api_key>
GORGIAS_USERNAME=<production_email>
GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/
DEBUG=false
RAILWAY_ENVIRONMENT=production
```

#### Staging Environment Variables:
```
GORGIAS_API_KEY=<staging_api_key>  # Can use same or test API key
GORGIAS_USERNAME=<staging_email>
GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/
DEBUG=true
RAILWAY_ENVIRONMENT=staging
```

#### Development Environment Variables:
```
GORGIAS_API_KEY=<dev_api_key>  # Can use test API key
GORGIAS_USERNAME=<dev_email>
GORGIAS_BASE_URL=https://petstoredirect.gorgias.com/api/
DEBUG=true
RAILWAY_ENVIRONMENT=development
```

## 🔄 Deployment Workflow

### Development Flow:

```bash
# 1. Work on feature branch
git checkout develop
git checkout -b feature/ticket-assignment-fix

# 2. Make changes and commit
git add .
git commit -m "Fix ticket assignment"

# 3. Push feature branch
git push origin feature/ticket-assignment-fix

# 4. Create PR to develop branch
# 5. After PR approval, merge to develop
# 6. Railway auto-deploys to Development environment
```

### Staging Flow:

```bash
# 1. Merge develop to staging (after testing in dev)
git checkout staging
git merge develop
git push origin staging

# 2. Railway auto-deploys to Staging environment
# 3. Perform integration testing
# 4. Test with real-world scenarios
```

### Production Flow:

```bash
# 1. Merge staging to main (after staging approval)
git checkout main
git merge staging
git push origin main

# 2. Railway auto-deploys to Production environment
# 3. Monitor production logs
# 4. Verify production deployment
```

## 📊 Environment Comparison

| Environment | Branch | Purpose | Auto-Deploy | Debug | Testing Level |
|------------|--------|---------|-------------|-------|---------------|
| **Development** | `develop` | Active development | ✅ Yes | ✅ Enabled | Unit tests, basic integration |
| **Staging** | `staging` | Pre-production | ✅ Yes | ✅ Enabled | Full integration, UAT |
| **Production** | `main` | Live production | ✅ Yes | ❌ Disabled | Production monitoring |

## 🛡️ Best Practices

### 1. **Never Deploy Directly to Production**
- Always go through: `develop` → `staging` → `main`
- Use PRs for code review
- Require approvals for production merges

### 2. **Environment-Specific Configuration**
- Use different API keys if possible (test vs production)
- Enable debug logging in dev/staging only
- Use `RAILWAY_ENVIRONMENT` variable to distinguish environments

### 3. **Monitoring & Alerts**
- Set up Railway alerts for each environment
- Monitor error rates in production
- Track deployment success/failure

### 4. **Rollback Strategy**
```bash
# If production deployment fails:
git checkout main
git revert <commit-hash>
git push origin main
# Railway will auto-deploy the reverted version
```

### 5. **Feature Flags** (Optional)
Consider using environment variables for feature flags:
```
ENABLE_NEW_ASSIGNMENT_LOGIC=true  # Only in staging/develop
ENABLE_EXPERIMENTAL_FEATURE=false # Disabled in production
```

## 🔍 Verification Checklist

### After Each Deployment:

#### Development:
- [ ] Server starts successfully
- [ ] Health check passes (`/health`)
- [ ] MCP tools are accessible
- [ ] Can create/update tickets
- [ ] Debug logs are visible

#### Staging:
- [ ] All development tests pass
- [ ] Integration tests pass
- [ ] Can assign tickets to agents
- [ ] Performance is acceptable
- [ ] No critical errors in logs

#### Production:
- [ ] All staging tests passed
- [ ] Production API credentials work
- [ ] Health check passes
- [ ] MCP endpoint responds correctly
- [ ] Monitoring shows healthy status
- [ ] No errors in production logs

## 📝 Git Workflow Commands

### Daily Development:
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Work and commit
git add .
git commit -m "Add feature X"
git push origin feature/my-feature

# Create PR: feature/my-feature → develop
```

### Promote to Staging:
```bash
# Merge develop to staging
git checkout staging
git pull origin staging
git merge develop
git push origin staging
# Railway auto-deploys staging
```

### Promote to Production:
```bash
# Merge staging to main
git checkout main
git pull origin main
git merge staging
git push origin main
# Railway auto-deploys production
```

## 🚨 Emergency Hotfix Process

For critical production fixes:

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-fix

# 2. Fix the issue
git add .
git commit -m "Hotfix: Critical issue"

# 3. Merge to main AND develop
git checkout main
git merge hotfix/critical-fix
git push origin main

git checkout develop
git merge hotfix/critical-fix
git push origin develop

# 4. Delete hotfix branch
git branch -d hotfix/critical-fix
```

## 📚 Additional Resources

- [Railway Branch Deployments](https://docs.railway.app/deploy/builds#branch-deployments)
- [Railway Environment Variables](https://docs.railway.app/deploy/variables)
- [Git Flow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## 🎯 Summary

This setup provides:
- ✅ **Clear separation** between environments
- ✅ **Automated deployments** from git branches
- ✅ **Disciplined workflow** (develop → staging → production)
- ✅ **Easy rollback** capabilities
- ✅ **Environment-specific** configuration
- ✅ **Production safety** (no direct production deploys)

Your Railway environments are now set up for professional, disciplined deployments! 🚀

