#!/bin/bash
# Startup script for Hugging Face Spaces deployment
# Ensures proper initialization and debugging

set -e

echo "===== TDS Quiz Solver Startup ====="
echo "Timestamp: $(date)"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python --version)"
echo "Port: ${PORT:-7860}"
echo ""

# Verify environment variables
echo "=== Environment Check ==="
if [ -z "$EMAIL" ]; then
    echo "⚠️  WARNING: EMAIL not set"
else
    echo "✅ EMAIL: $EMAIL"
fi

if [ -z "$SECRET" ]; then
    echo "⚠️  WARNING: SECRET not set"
else
    echo "✅ SECRET: ***${SECRET: -3}"
fi

if [ -n "$PIPE_TOKEN" ]; then
    echo "✅ PIPE_TOKEN: Configured"
else
    echo "ℹ️  PIPE_TOKEN: Not set (optional)"
fi
echo ""

# Check if Playwright browsers are installed
echo "=== Playwright Check ==="
if python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch(headless=True).close()" 2>/dev/null; then
    echo "✅ Playwright Chromium: Ready"
else
    echo "⚠️  Playwright Chromium: Not available (will use fallback mode)"
fi
echo ""

# Test health endpoint in background
echo "=== Starting Server ==="
export PORT=${PORT:-7860}
echo "Starting uvicorn on 0.0.0.0:$PORT"

# Start uvicorn
exec uvicorn main:app --host 0.0.0.0 --port $PORT
