#!/bin/bash

# PersonaForge AI - Full Stack Startup Script
# This script starts both the backend API server and the frontend development server

echo "🚀 Starting PersonaForge AI - Full Stack Application"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed. Please install npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🐍 Activating Python virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if frontend directory exists
if [ ! -d "personaforge-frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found. Please run the frontend setup first.${NC}"
    exit 1
fi

# Install frontend dependencies
echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
cd personaforge-frontend
npm install
cd ..

# Check if ports are available
echo -e "${BLUE}🔍 Checking port availability...${NC}"

if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Backend server may already be running.${NC}"
else
    echo -e "${GREEN}✅ Port 8000 is available for backend${NC}"
fi

if port_in_use 5173; then
    echo -e "${YELLOW}⚠️  Port 5173 is already in use. Frontend server may already be running.${NC}"
else
    echo -e "${GREEN}✅ Port 5173 is available for frontend${NC}"
fi

# Function to start backend server
start_backend() {
    echo -e "${BLUE}🔧 Starting backend server on port 8000...${NC}"
    python3 start_server.py &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
}

# Function to start frontend server
start_frontend() {
    echo -e "${BLUE}🎨 Starting frontend server on port 5173...${NC}"
    cd personaforge-frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend server stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend server stopped${NC}"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start servers
echo -e "\n${BLUE}🚀 Starting servers...${NC}"
start_backend
sleep 2
start_frontend

echo -e "\n${GREEN}🎉 PersonaForge AI is now running!${NC}"
echo -e "${BLUE}📱 Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "${BLUE}🔧 Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for user to stop
wait 