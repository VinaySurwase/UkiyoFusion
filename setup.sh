#!/bin/bash

echo "🎨 UkiyoFusion - Full Stack Image Transformation Platform"
echo "========================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Setting up UkiyoFusion development environment...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed.${NC}"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=postgresql://ukiyoe_user:ukiyoe_pass@db:5432/ukiyoe_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=ukiyoe-images
AWS_REGION=us-east-1

# Hugging Face Configuration
HF_TOKEN=your-huggingface-token

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# API Configuration
API_BASE_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✅ Created .env file. Please update it with your configuration.${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists.${NC}"
fi

# Install backend dependencies
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Created Python virtual environment.${NC}"
fi

source venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed.${NC}"
cd ..

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install
echo -e "${GREEN}✅ Frontend dependencies installed.${NC}"
cd ..

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p data/postgres
mkdir -p data/redis
echo -e "${GREEN}✅ Directories created.${NC}"

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Update the .env file with your configuration"
echo "2. Start the development environment:"
echo "   ${YELLOW}docker-compose up -d${NC}"
echo "3. Run database migrations:"
echo "   ${YELLOW}cd backend && source venv/bin/activate && flask db upgrade${NC}"
echo "4. Start the frontend development server:"
echo "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5000"
echo "API Documentation: http://localhost:5000/api/docs"
echo ""
echo -e "${YELLOW}💡 For production deployment, see the deployment guide in README.md${NC}"
