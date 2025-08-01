#!/bin/bash

echo "🎨 UkiyoeFusion - Quick Start (Fallback Mode)"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please run ./run.sh first.${NC}"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Flask backend (fallback version)
echo -e "${BLUE}🚀 Starting Flask backend (fallback mode) on port 5001...${NC}"
python app_fallback.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start React frontend on port 3001
echo -e "${BLUE}🚀 Starting React frontend on port 3001...${NC}"
cd frontend
PORT=3001 npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Both servers are running in fallback mode!${NC}"
echo -e "${BLUE}📱 Frontend: http://localhost:3001${NC}"
echo -e "${BLUE}🔧 Backend: http://localhost:5001${NC}"
echo -e "${YELLOW}Note: ControlNet features are disabled in fallback mode${NC}"
echo -e "${YELLOW}To enable ControlNet, wait for the full installation to complete${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for background processes
wait
