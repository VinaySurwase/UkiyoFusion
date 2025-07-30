#!/bin/bash

echo "🛑 Stopping UkiyoFusion servers..."

# Kill processes on ports 5001 and 8081
echo "Stopping backend server (port 5001)..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || echo "No backend process found"

echo "Stopping frontend server (port 8081)..."
lsof -ti:8081 | xargs kill -9 2>/dev/null || echo "No frontend process found"

sleep 1

echo "✅ All UkiyoFusion servers stopped!"
