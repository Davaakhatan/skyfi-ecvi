#!/bin/bash
# Comprehensive test runner for frontend with backend
# This script runs all frontend tests (unit + E2E) with proper backend setup

set -e

echo "🧪 Running Frontend Tests with Backend"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Must run from frontend directory${NC}"
    exit 1
fi

# Parse arguments
RUN_UNIT=true
RUN_E2E=true
COVERAGE=false
WATCH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_UNIT=true
            RUN_E2E=false
            shift
            ;;
        --e2e-only)
            RUN_UNIT=false
            RUN_E2E=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    bash scripts/test-teardown.sh
}

trap cleanup EXIT

# Run unit tests
if [ "$RUN_UNIT" = true ]; then
    echo -e "\n${BLUE}📝 Running Unit Tests${NC}"
    echo "-----------------------------------"
    
    if [ "$COVERAGE" = true ]; then
        npm run test:coverage
    elif [ "$WATCH" = true ]; then
        npm run test:ui
    else
        npm run test:unit
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Unit tests passed${NC}"
    else
        echo -e "${RED}❌ Unit tests failed${NC}"
        exit 1
    fi
fi

# Run E2E tests
if [ "$RUN_E2E" = true ]; then
    echo -e "\n${BLUE}🌐 Running E2E Tests${NC}"
    echo "-----------------------------------"
    echo "Note: E2E tests will start backend and frontend automatically"
    
    npm run test:e2e
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ E2E tests passed${NC}"
    else
        echo -e "${RED}❌ E2E tests failed${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}✅ All tests completed successfully!${NC}"

