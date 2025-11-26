#!/bin/bash
# CI Deployment Monitor for Gorgias MCP Server
# Monitors Cloud Build builds and Cloud Run deployments

set +e  # Don't exit on errors, we want to show all statuses

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
SERVICE_NAME="gorgias-mcp-server"
REGION="us-central1"
REFRESH_INTERVAL=10  # seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 CI Deployment Monitor${NC}"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Refresh interval: ${REFRESH_INTERVAL}s"
echo ""

# Function to check Cloud Build status
check_builds() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 Cloud Build Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check for ongoing builds
    ONGOING=$(gcloud builds list --ongoing --limit=5 --format="table(id,status,createTime,source.repoSource.branchName)" 2>&1)
    
    if echo "$ONGOING" | grep -q "ID"; then
        echo -e "${YELLOW}⏳ Ongoing builds:${NC}"
        echo "$ONGOING" | tail -n +2
    else
        echo -e "${GREEN}✅ No ongoing builds${NC}"
    fi
    
    # Show recent builds
    echo -e "\n${BLUE}Recent builds:${NC}"
    gcloud builds list --limit=5 --format="table(id,status,createTime,duration,source.repoSource.branchName,logUrl)" 2>&1 | head -6
    
    # Get latest build ID
    LATEST_BUILD=$(gcloud builds list --limit=1 --format="value(id)" 2>&1)
    
    if [ ! -z "$LATEST_BUILD" ] && [ "$LATEST_BUILD" != "Listed 0 items" ]; then
        echo -e "\n${BLUE}Latest build details:${NC}"
        BUILD_STATUS=$(gcloud builds describe "$LATEST_BUILD" --format="value(status)" 2>&1)
        BUILD_TIME=$(gcloud builds describe "$LATEST_BUILD" --format="value(createTime)" 2>&1)
        BUILD_LOG=$(gcloud builds describe "$LATEST_BUILD" --format="value(logUrl)" 2>&1)
        
        if [ "$BUILD_STATUS" = "SUCCESS" ]; then
            echo -e "Status: ${GREEN}✅ $BUILD_STATUS${NC}"
        elif [ "$BUILD_STATUS" = "FAILURE" ]; then
            echo -e "Status: ${RED}❌ $BUILD_STATUS${NC}"
        else
            echo -e "Status: ${YELLOW}⏳ $BUILD_STATUS${NC}"
        fi
        
        echo "Time: $BUILD_TIME"
        echo "Log: $BUILD_LOG"
    fi
}

# Function to check GitHub Actions workflows
check_github_actions() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🐙 GitHub Actions CI Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check if gh CLI is available
    if command -v gh &> /dev/null; then
        # Check if authenticated
        if gh auth status &> /dev/null; then
            echo -e "${BLUE}Recent workflow runs:${NC}"
            gh run list --limit=5 2>&1 || echo "No workflow runs found or not in a git repository"
        else
            echo -e "${YELLOW}⚠️  GitHub CLI not authenticated. Run: gh auth login${NC}"
            echo "View workflows at: https://github.com/$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]\(.*\)\.git/\1/' || echo 'OWNER/REPO')/actions"
        fi
    else
        echo -e "${YELLOW}⚠️  GitHub CLI (gh) not installed${NC}"
        echo "Install: brew install gh"
        echo "Or view workflows in GitHub web interface"
    fi
}

# Function to check Cloud Run service status
check_service() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 Cloud Run Service Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    SERVICE_INFO=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="yaml" 2>&1)
    
    if echo "$SERVICE_INFO" | grep -q "ERROR"; then
        echo -e "${RED}❌ Service '$SERVICE_NAME' not found in region $REGION${NC}"
        echo "Run: gcloud run services list --region=$REGION"
    else
        URL=$(echo "$SERVICE_INFO" | grep -A1 "url:" | tail -1 | awk '{print $2}')
        READY=$(echo "$SERVICE_INFO" | grep "ready:" | head -1 | awk '{print $2}')
        LATEST_REVISION=$(echo "$SERVICE_INFO" | grep "latestReadyRevisionName:" | awk '{print $2}')
        
        echo -e "Service: ${GREEN}$SERVICE_NAME${NC}"
        echo "URL: $URL"
        echo "Ready: $READY"
        echo "Latest Revision: $LATEST_REVISION"
        
        # Check health
        if [ ! -z "$URL" ]; then
            echo -e "\n${BLUE}Health check:${NC}"
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health" 2>&1 || echo "000")
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "Status: ${GREEN}✅ Healthy (HTTP $HTTP_CODE)${NC}"
            else
                echo -e "Status: ${RED}❌ Unhealthy (HTTP $HTTP_CODE)${NC}"
            fi
        fi
        
        # Show recent revisions
        echo -e "\n${BLUE}Recent revisions:${NC}"
        gcloud run revisions list --service="$SERVICE_NAME" --region="$REGION" --limit=3 --format="table(metadata.name,status.conditions[0].status,spec.containers[0].image)" 2>&1
    fi
}

# Function to show logs
show_logs() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 Recent Logs (last 10 lines)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    LOGS=$(gcloud run services logs read "$SERVICE_NAME" --region="$REGION" --limit=10 2>&1)
    if echo "$LOGS" | grep -q "ERROR\|not found"; then
        echo "No logs available (service may not be deployed yet)"
    else
        echo "$LOGS" | tail -10
    fi
}

# Main monitoring loop
if [ "$1" = "--once" ]; then
    # Single run mode
    check_builds
    check_github_actions
    check_service
    show_logs
else
    # Continuous monitoring mode
    while true; do
        clear
        echo -e "${BLUE}🔄 Monitoring CI/CD Pipeline${NC}"
        echo "Press Ctrl+C to stop"
        echo ""
        
        check_builds
        check_github_actions
        check_service
        show_logs
        
        echo -e "\n${YELLOW}⏳ Refreshing in ${REFRESH_INTERVAL} seconds...${NC}"
        sleep "$REFRESH_INTERVAL"
    done
fi

