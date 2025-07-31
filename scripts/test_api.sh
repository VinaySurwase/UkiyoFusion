#!/bin/bash

echo "🧪 UkiyoeFusion Test Script"
echo "=========================="

# Test API endpoints
API_URL="http://localhost:5000"

echo "Testing API endpoints..."

# Test health endpoint
echo "1. Testing health endpoint..."
response=$(curl -s -w "%{http_code}" "$API_URL/api/health")
http_code="${response: -3}"
if [ "$http_code" -eq 200 ]; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed (HTTP $http_code)"
fi

# Test models endpoint
echo "2. Testing models endpoint..."
response=$(curl -s -w "%{http_code}" "$API_URL/api/models")
http_code="${response: -3}"
if [ "$http_code" -eq 200 ]; then
    echo "   ✅ Models endpoint working"
else
    echo "   ❌ Models endpoint failed (HTTP $http_code)"
fi

# Test styles endpoint
echo "3. Testing styles endpoint..."
response=$(curl -s -w "%{http_code}" "$API_URL/api/styles")
http_code="${response: -3}"
if [ "$http_code" -eq 200 ]; then
    echo "   ✅ Styles endpoint working"
else
    echo "   ❌ Styles endpoint failed (HTTP $http_code)"
fi

echo ""
echo "📝 Test Summary:"
echo "================"
echo "Make sure both backend and frontend are running:"
echo "- Backend: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "If any tests failed, check:"
echo "1. Is the Flask server running?"
echo "2. Are all dependencies installed?"
echo "3. Check the logs for error messages"
