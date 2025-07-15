#!/bin/bash

# PersonaForge AI Startup Script
# This script activates the virtual environment and starts the server

echo "🚀 Starting PersonaForge AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the setup first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Kill any existing processes on port 8080
echo "🔄 Checking for existing processes on port 8080..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start the server
echo "🌐 Starting server on http://localhost:8080"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python3 -c "from web_dashboard import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8080)" 