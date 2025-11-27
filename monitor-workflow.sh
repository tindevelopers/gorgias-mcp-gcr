#!/bin/bash
# Monitor a specific GitHub Actions workflow run until completion

set +e

WORKFLOW_RUN_ID=${1:-"19699078979"}
REFRESH_INTERVAL=15  # seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔍 Monitoring GitHub Actions Workflow${NC}"
echo "Workflow Run ID: $WORKFLOW_RUN_ID"
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

# Function to get workflow status
get_status() {
    gh run view "$WORKFLOW_RUN_ID" --json status,conclusion,name,headBranch,createdAt,updatedAt,url,workflowName,jobs --jq '{
        status: .status,
        conclusion: .conclusion,
        name: .name,
        branch: .headBranch,
        createdAt: .createdAt,
        updatedAt: .updatedAt,
        url: .url,
        workflow: .workflowName,
        jobs: [.jobs[] | {
            name: .name,
            status: .status,
            conclusion: .conclusion,
            startedAt: .startedAt,
            completedAt: .completedAt
        }]
    }' 2>&1
}

# Function to display status
display_status() {
    local json_data="$1"
    
    clear
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🔍 GitHub Actions Workflow Monitor${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Parse and display workflow info
    local status=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null)
    local conclusion=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('conclusion', 'none'))" 2>/dev/null)
    local name=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('name', 'Unknown'))" 2>/dev/null)
    local branch=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('branch', 'unknown'))" 2>/dev/null)
    local url=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('url', ''))" 2>/dev/null)
    local workflow=$(echo "$json_data" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('workflow', 'Unknown'))" 2>/dev/null)
    
    echo -e "${BLUE}Workflow:${NC} $workflow"
    echo -e "${BLUE}Run Name:${NC} $name"
    echo -e "${BLUE}Branch:${NC} $branch"
    echo -e "${BLUE}URL:${NC} $url"
    echo ""
    
    # Display status
    if [ "$status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            echo -e "Status: ${GREEN}✅ COMPLETED - SUCCESS${NC}"
        elif [ "$conclusion" = "failure" ]; then
            echo -e "Status: ${RED}❌ COMPLETED - FAILURE${NC}"
        elif [ "$conclusion" = "cancelled" ]; then
            echo -e "Status: ${YELLOW}⚠️  COMPLETED - CANCELLED${NC}"
        else
            echo -e "Status: ${YELLOW}⚠️  COMPLETED - $conclusion${NC}"
        fi
    elif [ "$status" = "in_progress" ] || [ "$status" = "queued" ]; then
        echo -e "Status: ${CYAN}⏳ $status${NC}"
    else
        echo -e "Status: ${YELLOW}⚠️  $status${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 Jobs Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Display jobs
    echo "$json_data" | python3 -c "
import sys, json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    jobs = data.get('jobs', [])
    
    for job in jobs:
        name = job.get('name', 'Unknown')
        status = job.get('status', 'unknown')
        conclusion = job.get('conclusion', 'none')
        
        status_icon = '⏳'
        status_color = '\033[0;36m'  # Cyan
        
        if status == 'completed':
            if conclusion == 'success':
                status_icon = '✅'
                status_color = '\033[0;32m'  # Green
            elif conclusion == 'failure':
                status_icon = '❌'
                status_color = '\033[0;31m'  # Red
            elif conclusion == 'cancelled':
                status_icon = '⚠️'
                status_color = '\033[1;33m'  # Yellow
            else:
                status_icon = '⚠️'
                status_color = '\033[1;33m'  # Yellow
        
        print(f'{status_color}{status_icon}{'\033[0m'} {name:30s} {status_color}{status:12s}{'\033[0m'} {conclusion}')
        
except Exception as e:
    print(f'Error parsing jobs: {e}')
    print(json.dumps(json.load(sys.stdin), indent=2))
" 2>/dev/null || echo "$json_data"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Return status for loop control
    if [ "$status" = "completed" ]; then
        return 0
    else
        return 1
    fi
}

# Main monitoring loop
while true; do
    STATUS_DATA=$(get_status)
    
    if echo "$STATUS_DATA" | grep -q "error\|not found"; then
        echo -e "${RED}❌ Error fetching workflow status${NC}"
        echo "$STATUS_DATA"
        exit 1
    fi
    
    display_status "$STATUS_DATA"
    
    # Check if completed
    STATUS=$(echo "$STATUS_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo -e "${GREEN}🎉 Workflow completed!${NC}"
        
        CONCLUSION=$(echo "$STATUS_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conclusion', 'none'))" 2>/dev/null)
        
        if [ "$CONCLUSION" = "success" ]; then
            echo -e "${GREEN}✅ All checks passed!${NC}"
        else
            echo -e "${RED}❌ Workflow failed. Check the logs for details.${NC}"
            echo ""
            echo "View logs: gh run view $WORKFLOW_RUN_ID --log"
            echo "Or visit: $(echo "$STATUS_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', ''))" 2>/dev/null)"
        fi
        
        break
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Refreshing in ${REFRESH_INTERVAL} seconds... (Press Ctrl+C to stop)${NC}"
    sleep "$REFRESH_INTERVAL"
done


