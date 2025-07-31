#!/bin/bash

echo "🎨 UkiyoeFusion Setup Script"
echo "==========================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 14 or higher"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    echo "Please install npm"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads models logs

# Setup frontend
echo "📦 Setting up React frontend..."
cd frontend
npm install
cd ..

# Make scripts executable
chmod +x run.sh
chmod +x scripts/model_manager.sh

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application, run:"
echo "./run.sh"
echo ""
echo "📚 To manage models, run:"
echo "./scripts/model_manager.sh"
