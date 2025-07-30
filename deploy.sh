#!/bin/bash

# UkiyoFusion Production Deployment Script
# This script handles the complete deployment process for production

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ukiyofusion"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    echo "[ERROR] $1" >> "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
    echo "[SUCCESS] $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
    echo "[WARNING] $1" >> "$LOG_FILE"
}

# Create log directory
mkdir -p logs

log "🚀 Starting UkiyoFusion production deployment..."

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    error "docker-compose.prod.yml not found. Please run this script from the project root."
fi

# Check prerequisites
log "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
fi

success "All prerequisites are installed."

# Check environment file
if [ ! -f ".env.prod" ]; then
    warning ".env.prod file not found. Creating template..."
    cat > .env.prod << 'EOF'
# Production Environment Configuration
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key
POSTGRES_PASSWORD=your-secure-postgres-password
REDIS_PASSWORD=your-secure-redis-password
GRAFANA_PASSWORD=your-grafana-admin-password

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=ukiyoe-images-prod

# Hugging Face Token
HF_TOKEN=your-huggingface-token

# Database Configuration
DATABASE_BACKUP_ENABLED=true
DATABASE_BACKUP_SCHEDULE=0 2 * * *
EOF
    warning "Please update .env.prod with your production values before continuing."
    exit 1
fi

log "✅ Environment configuration found."

# Build frontend for production
log "🏗️ Building frontend for production..."
cd frontend

if [ ! -f "package.json" ]; then
    error "package.json not found in frontend directory."
fi

# Install dependencies and build
npm ci --only=production
npm run build

if [ ! -d "dist" ]; then
    error "Frontend build failed. dist directory not found."
fi

success "Frontend built successfully."
cd ..

# Create backup of existing deployment
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    log "📦 Creating backup of existing deployment..."
    mkdir -p "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
    
    # Backup database
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ukiyoe_user ukiyoe_db > "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/database.sql"
    
    # Backup uploaded files
    if [ -d "backend/uploads" ]; then
        cp -r backend/uploads "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/"
    fi
    
    success "Backup created successfully."
fi

# Stop existing services
log "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
log "📥 Pulling latest base images..."
docker-compose -f docker-compose.prod.yml pull

# Build new images
log "🔨 Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
log "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
log "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
log "🏥 Performing health checks..."

# Check database
if ! docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U ukiyoe_user -d ukiyoe_db; then
    error "Database health check failed."
fi

# Check Redis
if ! docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping; then
    error "Redis health check failed."
fi

# Check backend
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    error "Backend health check failed."
fi

success "All health checks passed."

# Run database migrations
log "🗃️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade

# Create superuser if it doesn't exist
log "👤 Setting up admin user..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app import app, db
from models.user import User
import os

with app.app_context():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@ukiyofusion.com')
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            username='admin',
            email=admin_email,
            is_admin=True
        )
        admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user created: {admin_email}')
    else:
        print('Admin user already exists')
"

# Clear old Docker images
log "🧹 Cleaning up old Docker images..."
docker image prune -f

# Display deployment information
log "📊 Deployment completed successfully!"

echo ""
echo -e "${GREEN}🎉 UkiyoFusion is now running in production mode!${NC}"
echo ""
echo -e "${BLUE}📋 Service URLs:${NC}"
echo "Frontend: http://localhost"
echo "API: http://localhost/api"
echo "Grafana Dashboard: http://localhost:3001"
echo "Prometheus Metrics: http://localhost:9090"
echo ""
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo "View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "Scale service: docker-compose -f docker-compose.prod.yml up -d --scale celery=3"
echo "Update service: docker-compose -f docker-compose.prod.yml up -d --no-deps [service]"
echo "Backup database: docker-compose -f docker-compose.prod.yml exec db pg_dump -U ukiyoe_user ukiyoe_db > backup.sql"
echo ""
echo -e "${YELLOW}⚠️ Remember to:${NC}"
echo "1. Configure SSL certificates for HTTPS"
echo "2. Set up monitoring alerts"
echo "3. Configure automated backups"
echo "4. Review security settings"
echo ""

success "Deployment script completed successfully!"
