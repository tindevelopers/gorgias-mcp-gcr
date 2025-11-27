#!/bin/bash
# Monitor GitHub Actions builds for new commits until a successful build

set +e

BRANCH=${1:-"main"}
REFRESH_INTERVAL=20  # seconds
LAST_RUN_ID=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔍 Monitoring GitHub Actions Builds${NC}"
echo "Branch: $BRANCH"
echo "Watching for new commits and builds..."
echo "Refresh interval: ${REFRESH_INTERVAL}s"
echo "Press Ctrl+C to stop"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) not found${NC}"
    echo "Install: brew install gh"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Function to get latest workflow run
get_latest_run() {
    gh run list --workflow=CI --branch="$BRANCH" --limit=1 --json databaseId,status,conclusion,name,headBranch,createdAt,url,headSha --jq '.[0]' 2>&1
}

# Function to display run status
display_run() {
    local json_data="$1"
    
    local run_id=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('databaseId', ''))" 2>/dev/null)
    local status=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    local conclusion=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conclusion', 'none'))" 2>/dev/null)
    local name=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('name', 'Unknown'))" 2>/dev/null)
    local sha=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('headSha', '')[:7])" 2>/dev/null)
    local url=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', ''))" 2>/dev/null)
    local created=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('createdAt', ''))" 2>/dev/null)
    
    clear
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🔍 GitHub Actions Build Monitor${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}Branch:${NC} $BRANCH"
    echo -e "${BLUE}Commit:${NC} $sha"
    echo -e "${BLUE}Run ID:${NC} $run_id"
    echo -e "${BLUE}Created:${NC} $created"
    echo -e "${BLUE}URL:${NC} $url"
    echo ""
    
    # Display status
    if [ "$status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            echo -e "Status: ${GREEN}✅ COMPLETED - SUCCESS${NC}"
            echo ""
            echo -e "${GREEN}🎉 Build successful!${NC}"
            return 0
        elif [ "$conclusion" = "failure" ]; then
            echo -e "Status: ${RED}❌ COMPLETED - FAILURE${NC}"
        elif [ "$conclusion" = "cancelled" ]; then
            echo -e "Status: ${YELLOW}⚠️  COMPLETED - CANCELLED${NC}"
        else
            echo -e "Status: ${YELLOW}⚠️  COMPLETED - $conclusion${NC}"
        fi
    elif [ "$status" = "in_progress" ]; then
        echo -e "Status: ${CYAN}⏳ IN PROGRESS${NC}"
    elif [ "$status" = "queued" ]; then
        echo -e "Status: ${CYAN}📋 QUEUED${NC}"
    else
        echo -e "Status: ${YELLOW}⚠️  $status${NC}"
    fi
    
    echo ""
    
    # Get detailed job status
    if [ ! -z "$run_id" ]; then
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}📋 Jobs Status${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        gh run view "$run_id" --json jobs --jq '.jobs[] | "\(.name)|\(.status)|\(.conclusion)"' 2>&1 | while IFS='|' read -r job_name job_status job_conclusion; do
            if [ "$job_status" = "completed" ]; then
                if [ "$job_conclusion" = "success" ]; then
                    echo -e "  ${GREEN}✅${NC} $job_name - ${GREEN}$job_status${NC} ($job_conclusion)"
                elif [ "$job_conclusion" = "failure" ]; then
                    echo -e "  ${RED}❌${NC} $job_name - ${RED}$job_status${NC} ($job_conclusion)"
                else
                    echo -e "  ${YELLOW}⚠️${NC}  $job_name - ${YELLOW}$job_status${NC} ($job_conclusion)"
                fi
            else
                echo -e "  ${CYAN}⏳${NC} $job_name - ${CYAN}$job_status${NC}"
            fi
        done
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    return 1
}

# Main monitoring loop
echo -e "${CYAN}Waiting for new builds...${NC}"
echo ""

while true; do
    LATEST_RUN=$(get_latest_run)
    
    if echo "$LATEST_RUN" | grep -q "error\|not found"; then
        echo -e "${RED}❌ Error fetching workflow runs${NC}"
        echo "$LATEST_RUN"
        sleep "$REFRESH_INTERVAL"
        continue
    fi
    
    CURRENT_RUN_ID=$(echo "$LATEST_RUN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('databaseId', ''))" 2>/dev/null)
    
    # Check if this is a new run
    if [ "$CURRENT_RUN_ID" != "$LAST_RUN_ID" ] && [ ! -z "$CURRENT_RUN_ID" ]; then
        if [ ! -z "$LAST_RUN_ID" ]; then
            echo -e "${CYAN}🆕 New build detected!${NC}"
            echo ""
        fi
        LAST_RUN_ID="$CURRENT_RUN_ID"
    fi
    
    display_run "$LATEST_RUN"
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        # Build succeeded!
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅ SUCCESS! Build completed successfully!${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        break
    fi
    
    STATUS=$(echo "$LATEST_RUN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    
    if [ "$STATUS" = "completed" ]; then
        CONCLUSION=$(echo "$LATEST_RUN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conclusion', 'none'))" 2>/dev/null)
        if [ "$CONCLUSION" != "success" ]; then
            echo ""
            echo -e "${YELLOW}⏳ Waiting for new commit to trigger a new build...${NC}"
            echo "Current build failed. Monitoring for next commit..."
        fi
    else
        echo ""
        echo -e "${CYAN}⏳ Build in progress... Refreshing in ${REFRESH_INTERVAL}s${NC}"
    fi
    
    sleep "$REFRESH_INTERVAL"
done


