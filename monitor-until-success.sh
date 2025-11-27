#!/bin/bash
# Monitor CI builds until one succeeds

set +e

BRANCH=${1:-"main"}
MAX_ITERATIONS=${2:-10}
ITERATION=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 Monitoring CI until success${NC}"
echo "Branch: $BRANCH"
echo "Max iterations: $MAX_ITERATIONS"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) not found${NC}"
    exit 1
fi

# Function to get latest workflow run
get_latest_run() {
    gh run list --workflow=CI --branch="$BRANCH" --limit=1 --json databaseId,status,conclusion,name,headBranch,createdAt,url,headSha 2>&1
}

# Function to display status
display_status() {
    local json_data="$1"
    local iteration="$2"
    
    clear
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🔄 CI Build Monitor - Iteration $iteration/$MAX_ITERATIONS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    local run_id=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('databaseId', ''))" 2>/dev/null)
    local status=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    local conclusion=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conclusion', 'none'))" 2>/dev/null)
    local sha=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('headSha', '')[:7])" 2>/dev/null)
    local url=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', ''))" 2>/dev/null)
    local created=$(echo "$json_data" | python3 -c "import sys, json; print(json.load(sys.stdin).get('createdAt', ''))" 2>/dev/null)
    
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
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}🎉 SUCCESS! CI passed!${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            return 0
        elif [ "$conclusion" = "failure" ]; then
            echo -e "Status: ${RED}❌ COMPLETED - FAILURE${NC}"
            return 1
        else
            echo -e "Status: ${YELLOW}⚠️  COMPLETED - $conclusion${NC}"
            return 1
        fi
    elif [ "$status" = "in_progress" ]; then
        echo -e "Status: ${CYAN}⏳ IN PROGRESS${NC}"
        return 2
    elif [ "$status" = "queued" ]; then
        echo -e "Status: ${CYAN}📋 QUEUED${NC}"
        return 2
    else
        echo -e "Status: ${YELLOW}⚠️  $status${NC}"
        return 2
    fi
}

# Main monitoring loop
while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    
    LATEST_RUN=$(get_latest_run)
    
    if echo "$LATEST_RUN" | grep -q "error\|not found"; then
        echo -e "${RED}❌ Error fetching workflow runs${NC}"
        sleep 10
        continue
    fi
    
    display_status "$LATEST_RUN" "$ITERATION"
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        # Success!
        exit 0
    elif [ $RESULT -eq 1 ]; then
        # Failed - show job details
        RUN_ID=$(echo "$LATEST_RUN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('databaseId', ''))" 2>/dev/null)
        if [ ! -z "$RUN_ID" ]; then
            echo ""
            echo -e "${BLUE}Job Status:${NC}"
            gh run view "$RUN_ID" --json jobs --jq '.jobs[] | "\(.name): \(.status) - \(.conclusion)"' 2>&1 | while read -r line; do
                if echo "$line" | grep -q "failure"; then
                    echo -e "  ${RED}❌ $line${NC}"
                elif echo "$line" | grep -q "success"; then
                    echo -e "  ${GREEN}✅ $line${NC}"
                else
                    echo -e "  ${YELLOW}⏳ $line${NC}"
                fi
            done
        fi
        
        if [ $ITERATION -ge $MAX_ITERATIONS ]; then
            echo ""
            echo -e "${RED}❌ Max iterations reached. CI did not pass.${NC}"
            exit 1
        fi
        
        echo ""
        echo -e "${YELLOW}⏳ Waiting for next check... (15s)${NC}"
        sleep 15
    else
        # In progress
        echo ""
        echo -e "${CYAN}⏳ Build in progress... Checking again in 20s${NC}"
        sleep 20
    fi
done

echo -e "${RED}❌ Max iterations reached${NC}"
exit 1


