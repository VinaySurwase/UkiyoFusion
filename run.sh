#!/bin/bash

echo "🎨 UkiyoeFusion - Starting Image Transformation App"
echo "=================================================="

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

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Install Node.js dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Create uploads directory
mkdir -p uploads

echo -e "${GREEN}✅ Setup complete!${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Flask backend on alternate port
echo -e "${BLUE}🚀 Starting Flask backend on port 5001...${NC}"
FLASK_RUN_PORT=5001 python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start React frontend on alternate port
echo -e "${BLUE}🚀 Starting React frontend on port 3000...${NC}"
cd frontend
PORT=3000 npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Both servers are running!${NC}"
echo -e "${BLUE}📱 Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend: http://localhost:5001${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for background processes
wait
