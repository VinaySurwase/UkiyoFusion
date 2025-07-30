#!/bin/bash

# UkiyoFusion Startup Script
# This script starts both the backend and frontend servers

echo "🎌 Starting UkiyoFusion Application..."
echo "========================================="

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down UkiyoFusion..."
    
    # Kill backend process
    if [[ ! -z $BACKEND_PID ]]; then
        echo "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend process
    if [[ ! -z $FRONTEND_PID ]]; then
        echo "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Kill any remaining processes on ports 5001 and 8081
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    lsof -ti:8081 | xargs kill -9 2>/dev/null
    
    echo "✅ UkiyoFusion stopped successfully!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [[ ! -d "backend" ]] || [[ ! -d "simple_frontend" ]]; then
    echo "❌ Error: Please run this script from the UkiyoFusion directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -f "backend/simple_venv/bin/python" ]]; then
    echo "❌ Error: Virtual environment not found at backend/simple_venv/"
    echo "   Please make sure the virtual environment is set up correctly"
    exit 1
fi

# Kill any existing processes on the ports
echo "🧹 Cleaning up any existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:8081 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend server
echo "🚀 Starting backend server..."
cd backend
./simple_venv/bin/python simple_app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Error: Backend server failed to start"
    echo "Check logs/backend.log for details"
    exit 1
fi

echo "✅ Backend server started (PID: $BACKEND_PID) on http://localhost:5001"

# Start frontend server
echo "🚀 Starting frontend server..."
cd simple_frontend
python3 -m http.server 8081 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 2

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Error: Frontend server failed to start"
    echo "Check logs/frontend.log for details"
    cleanup
    exit 1
fi

echo "✅ Frontend server started (PID: $FRONTEND_PID) on http://localhost:8081"
echo ""
echo "🎉 UkiyoFusion is now running!"
echo "========================================="
echo "🌐 Frontend: http://localhost:8081"
echo "⚙️  Backend:  http://localhost:5001"
echo "📝 Logs:     logs/backend.log and logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================="

# Keep the script running and wait for user input
while true; do
    sleep 1
    
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly"
        cleanup
        exit 1
    fi
done
