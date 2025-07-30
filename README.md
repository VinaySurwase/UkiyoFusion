# UkiyoFusion 🎨

A production-ready full-stack web application for AI-powered image-to-image transformations using diffusion models. Transform your images with the artistic style of Japanese Ukiyo-e paintings and other creative styles.

## � Features

- **AI-Powered Image Transformation**: Leverage state-of-the-art diffusion models for image-to-image transformations
- **Multiple Art Styles**: Support for various artistic styles including Ukiyo-e, modern art, and custom styles
- **Real-time Processing**: WebSocket-based real-time updates during image processing
- **User Authentication**: Secure JWT-based authentication system
- **Gallery Management**: Personal and public galleries to showcase transformations
- **Background Processing**: Asynchronous task processing with Celery and Redis
- **Cloud Storage**: AWS S3 integration for scalable image storage
- **Responsive Design**: Mobile-first responsive design with Tailwind CSS
- **Production Ready**: Docker containerization and nginx proxy configuration
- **User Authentication**: Secure user accounts with JWT authentication
- **Responsive Design**: Mobile-first approach with modern UI/UX
- **Production Ready**: Containerized deployment with monitoring and logging

## 🏗️ Architecture

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: Zustand for global state
- **HTTP Client**: Axios with interceptors
- **File Upload**: React Dropzone with progress tracking
- **UI Components**: Headless UI + custom components
- **WebSocket**: Real-time updates during processing

### Backend (Flask + Python)

- **Framework**: Flask with Flask-RESTful
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis for session management and caching
- **Queue**: Celery for background processing
- **Authentication**: JWT with Flask-JWT-Extended
- **File Storage**: AWS S3 compatible storage
- **AI Models**: Hugging Face Diffusers for image processing

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx as reverse proxy
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with ELK stack
- **CI/CD**: GitHub Actions workflows

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.9+ (for development)

### Development Setup

1. **Clone and setup**:

```bash
git clone <repository-url>
cd UkiyoFusion
cp .env.example .env
```

2. **Start services**:

```bash
docker-compose up -d
```

3. **Frontend development**:

```bash
cd frontend
npm install
npm run dev
```

4. **Backend development**:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

### Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📱 API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `DELETE /api/auth/logout` - User logout

### Image Processing

- `POST /api/transform/upload` - Upload image for transformation
- `GET /api/transform/status/{task_id}` - Check processing status
- `GET /api/transform/result/{task_id}` - Get transformation result
- `GET /api/transform/history` - User's transformation history

### Gallery

- `GET /api/gallery` - Get user's gallery
- `POST /api/gallery` - Save transformation to gallery
- `DELETE /api/gallery/{id}` - Delete from gallery
- `PUT /api/gallery/{id}` - Update gallery item

## 🔧 Configuration

Environment variables are configured in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ukiyo_fusion

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key

# AWS S3 (or compatible)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=ukiyo-fusion-storage

# Hugging Face
HUGGINGFACE_TOKEN=your-hf-token
```

## 🎯 Model Configuration

The application supports multiple diffusion models:

- **Stable Diffusion XL**: High-quality general transformations
- **ControlNet**: Structure-preserving transformations
- **Custom Ukiyo-e Models**: Specialized for Japanese art style

## 📊 Monitoring

- **Application Metrics**: Prometheus metrics at `/metrics`
- **Health Checks**: `/health` endpoint for service monitoring
- **Logging**: Structured JSON logs with correlation IDs

## 🧪 Testing

```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && python -m pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For support and questions, please open an issue in the repository.
