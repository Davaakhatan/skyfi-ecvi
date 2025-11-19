#!/bin/bash
# Test teardown script - stops backend server

set -e

if [ -f /tmp/backend_test_pid.txt ]; then
    BACKEND_PID=$(cat /tmp/backend_test_pid.txt)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🛑 Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
        echo "✅ Backend server stopped"
    fi
    rm -f /tmp/backend_test_pid.txt
fi

# Clean up any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true

echo "🧹 Test environment cleaned up"

