#!/bin/bash
# AI Brand Studio - Vertex AI Agent Engine Deployment Script

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI Brand Studio - Agent Deployment${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if ADK is installed
if ! command -v adk &> /dev/null; then
    echo -e "${RED}ERROR: ADK (Agent Development Kit) not installed${NC}"
    echo "Install with: pip install google-genai"
    exit 1
fi

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}\n"

# Get configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Enter Google Cloud Project ID:${NC}"
    read PROJECT_ID
    export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
fi

echo -e "Project: ${GREEN}$PROJECT_ID${NC}"
echo -e "Region: ${GREEN}$REGION${NC}\n"

# Ensure we're authenticated
echo -e "${YELLOW}Checking authentication...${NC}"
gcloud config set project $PROJECT_ID

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
fi

echo -e "${GREEN}✓ Authenticated${NC}\n"

# Run tests before deployment
echo -e "${YELLOW}Running tests before deployment...${NC}"
echo "Would you like to run tests? (y/n)"
read -r RUN_TESTS

if [ "$RUN_TESTS" = "y" ] || [ "$RUN_TESTS" = "Y" ]; then
    echo -e "${YELLOW}Running Phase 2 tests...${NC}"
    python test_phase2.py || {
        echo -e "${RED}Tests failed! Fix errors before deploying.${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Tests passed${NC}\n"
fi

# Build deployment package
echo -e "${YELLOW}Preparing deployment package...${NC}"

# Create deployment directory
DEPLOY_DIR="deployment"
mkdir -p $DEPLOY_DIR

# Copy required files
echo "Copying source files..."
cp -r src/ $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp .agent_engine_config.json $DEPLOY_DIR/
cp README.md $DEPLOY_DIR/ 2>/dev/null || echo "No README found"

echo -e "${GREEN}✓ Deployment package ready${NC}\n"

# Deploy to Vertex AI Agent Engine
echo -e "${YELLOW}Deploying to Vertex AI Agent Engine...${NC}"
echo "This may take 5-10 minutes..."
echo ""

cd $DEPLOY_DIR

# Check if this is an update or new deployment
AGENT_NAME="brand_studio_agent"
EXISTING_AGENT=$(gcloud ai agents list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --filter="display_name:$AGENT_NAME" \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$EXISTING_AGENT" ]; then
    echo -e "${YELLOW}Existing agent found. Updating...${NC}"
    DEPLOY_CMD="update"
else
    echo -e "${YELLOW}Creating new agent deployment...${NC}"
    DEPLOY_CMD="deploy"
fi

# Deploy using ADK
adk $DEPLOY_CMD agent_engine \
    --project=$PROJECT_ID \
    --region=$REGION \
    $AGENT_NAME \
    --agent_engine_config_file=.agent_engine_config.json || {
    echo -e "${RED}Deployment failed!${NC}"
    cd ..
    exit 1
}

cd ..

echo -e "${GREEN}✓ Deployment complete${NC}\n"

# Get deployment info
echo -e "${YELLOW}Getting deployment information...${NC}"

AGENT_INFO=$(gcloud ai agents list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --filter="display_name:$AGENT_NAME" \
    --format="value(name,updateTime)" 2>/dev/null || echo "")

if [ -n "$AGENT_INFO" ]; then
    echo -e "${GREEN}Agent deployed successfully!${NC}\n"
    echo "Agent Information:"
    echo "$AGENT_INFO"
    echo ""

    # Get endpoint URL
    AGENT_ID=$(echo "$AGENT_INFO" | awk '{print $1}' | awk -F/ '{print $NF}')
    ENDPOINT_URL="https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/agents/${AGENT_ID}:query"

    echo -e "${YELLOW}API Endpoint:${NC}"
    echo "$ENDPOINT_URL"
    echo ""

    # Save deployment info
    cat > deployment/deployment_info.json << EOF
{
  "project_id": "$PROJECT_ID",
  "region": "$REGION",
  "agent_name": "$AGENT_NAME",
  "agent_id": "$AGENT_ID",
  "endpoint_url": "$ENDPOINT_URL",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    echo -e "${GREEN}✓ Deployment info saved to deployment/deployment_info.json${NC}"
fi

# Test deployment
echo -e "\n${YELLOW}Would you like to test the deployed agent? (y/n)${NC}"
read -r TEST_AGENT

if [ "$TEST_AGENT" = "y" ] || [ "$TEST_AGENT" = "Y" ]; then
    echo -e "${YELLOW}Testing agent with sample request...${NC}"

    TEST_QUERY="I need a brand name for an AI-powered fitness app for millennials."

    RESPONSE=$(gcloud ai agents query $AGENT_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --query="$TEST_QUERY" \
        --format=json 2>&1 || echo "Test failed")

    if [[ "$RESPONSE" == *"Test failed"* ]]; then
        echo -e "${RED}Test request failed. Check logs for details.${NC}"
    else
        echo -e "${GREEN}✓ Agent responding successfully${NC}"
        echo "Sample response:"
        echo "$RESPONSE" | head -20
    fi
fi

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo "Next steps:"
echo "1. Test your agent:"
echo "   gcloud ai agents query $AGENT_NAME --region=$REGION --query='Your test query'"
echo ""
echo "2. View logs:"
echo "   gcloud logging read \"resource.type=aiplatform.googleapis.com/Agent\" --limit=50"
echo ""
echo "3. Monitor performance:"
echo "   https://console.cloud.google.com/ai/agents?project=$PROJECT_ID"
echo ""

echo -e "${GREEN}Deployment successful! 🎉${NC}"
