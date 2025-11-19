#!/bin/bash
# Test setup script for frontend tests with backend
# This script starts the backend server and waits for it to be ready

set -e

BACKEND_DIR="../backend"
BACKEND_PORT=8000
FRONTEND_PORT=5173
MAX_WAIT=60

echo "🚀 Starting test environment setup..."

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Function to check if backend is ready
check_backend_ready() {
    curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null 2>&1
}

# Start backend server in background
echo "📦 Starting backend server..."
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing backend dependencies..."
    pip install -e ".[dev]" > /dev/null 2>&1
    touch .deps_installed
fi

# Set environment variables
export DATABASE_URL="${DATABASE_URL:-sqlite:///./test.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export SECRET_KEY="${SECRET_KEY:-test-secret-key-for-frontend-tests-minimum-32-chars}"
export CORS_ORIGINS="http://localhost:$FRONTEND_PORT"
export ENVIRONMENT="test"

# Start backend server
echo "Starting FastAPI server on port $BACKEND_PORT..."
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
WAIT_COUNT=0
while ! check_backend_ready; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo "❌ Backend failed to start within $MAX_WAIT seconds"
        echo "Backend logs:"
        cat /tmp/backend.log
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
done

echo ""
echo "✅ Backend is ready on http://localhost:$BACKEND_PORT"

# Return to frontend directory
cd - > /dev/null

# Export backend PID for cleanup
echo $BACKEND_PID > /tmp/backend_test_pid.txt

echo "✅ Test environment ready!"
echo "Backend PID: $BACKEND_PID"
echo "Backend URL: http://localhost:$BACKEND_PORT"
echo "Frontend URL: http://localhost:$FRONTEND_PORT"

