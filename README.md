# 🎨 UkiyoeFusion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

> Transform any image into authentic Ukiyo-e (traditional Japanese woodblock print) style using state-of-the-art AI technology.

UkiyoeFusion bridges the gap between modern photography and traditional Japanese art, allowing users to experience the timeless beauty of Ukiyo-e through cutting-edge artificial intelligence.

## ✨ Features

### 🎨 **Artistic Transformation**

- **Authentic Ukiyo-e Styles**: Six distinct traditional styles including Classic, Hokusai, Hiroshige, Utamaro, Kabuki, and Seasonal
- **Custom-trained Models**: Purpose-built AI models optimized for traditional Japanese art aesthetics
- **Smart Prompting**: Works beautifully with or without additional descriptive text

### 📱 **Modern Input Methods**

- **File Upload**: Standard drag-and-drop or click-to-browse functionality
- **Real-time Camera Capture**:
  - 📸 Direct photo capture within the application
  - 🔄 Front/back camera switching for mobile devices
  - 🎯 High-definition capture (1280x720 resolution)
  - 📱 Mobile-first responsive design
  - 🛡️ Secure permission-based camera access

### 🚀 **User Experience**

- **Intuitive Interface**: Clean, minimalist design focused on the art creation process
- **Instant Results**: Fast processing with optimized AI pipeline
- **Cross-platform**: Works seamlessly on desktop and mobile browsers

## 🛠️ Tech Stack

| Component            | Technology                     | Purpose                                 |
| -------------------- | ------------------------------ | --------------------------------------- |
| **Backend**          | Flask + PyTorch                | AI model serving and API endpoints      |
| **Frontend**         | React + Material-UI            | Modern, responsive user interface       |
| **AI Models**        | Stable Diffusion + Custom LoRA | Ukiyo-e style transformation engine     |
| **Image Processing** | Canvas API + WebRTC            | Real-time camera capture and processing |

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/VinaySurwase/UkiyoeFusion.git
cd UkiyoeFusion

# Make the run script executable and start everything
chmod +x run.sh
./run.sh
```

### Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs

## 📖 Usage Guide

### 🖼️ Image Input Methods

#### Traditional Upload

1. Click **"Choose File"** or drag and drop images into the upload area
2. Supported formats: JPEG, PNG, WebP (max 10MB)

#### Camera Capture

1. Click **"Take Photo"** button
2. Grant camera permissions when prompted by your browser
3. Use the live preview to frame your subject
4. Toggle between front/back cameras using the switch button
5. Click **"Capture Photo"** to take the picture
6. Your image is immediately ready for transformation

### 🎨 Transformation Workflow

1. **Select Input**: Upload a file or capture with camera
2. **Choose Style**: Pick from six authentic Ukiyo-e styles
3. **Add Context** _(Optional)_: Provide descriptive prompts for enhanced results
4. **Transform**: Click the transform button and wait for AI processing
5. **Download**: Save your traditional Japanese artwork

### 📋 Camera Feature Requirements

| Requirement      | Details                                      |
| ---------------- | -------------------------------------------- |
| **Protocol**     | HTTPS required in production environments    |
| **Permissions**  | User must explicitly grant camera access     |
| **Connectivity** | Active internet connection for AI processing |
| **Performance**  | Modern device with adequate processing power |

## ⚙️ Manual Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 16.0 or higher
- npm or yarn package manager

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Custom Models

```bash
# Add your custom models to the models directory
cp your_custom_model.safetensors models/
# Models are automatically detected and loaded
```

## 🔌 API Reference

### Endpoints

| Method | Endpoint         | Description                      | Parameters                            |
| ------ | ---------------- | -------------------------------- | ------------------------------------- |
| `POST` | `/api/transform` | Transform image to Ukiyo-e style | `image`, `style`, `prompt` (optional) |
| `GET`  | `/api/models`    | List available AI models         | None                                  |
| `GET`  | `/api/styles`    | List available Ukiyo-e styles    | None                                  |
| `GET`  | `/api/health`    | Service health check             | None                                  |

### Example Request

```bash
curl -X POST http://localhost:5000/api/transform \
  -F "image=@your_image.jpg" \
  -F "style=hokusai" \
  -F "prompt=mountain landscape at sunset"
```

## 👩‍💻 Development

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Frontend Development

```bash
cd frontend
npm install
npm start  # Development server with hot reload
```

### Backend Development

```bash
# Install in development mode
pip install -e .

# Run with debug mode
export FLASK_ENV=development
python app.py
```

### Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
python -m pytest tests/

# Run specific test file
npm test -- ImageUpload.test.js
```

### Code Quality

```bash
# Frontend linting
cd frontend
npm run lint

# Python code formatting
black .
flake8 .
```

## 🔒 Security & Privacy

### Data Protection

- **No Server Storage**: Images are processed in memory and immediately discarded
- **Local Processing**: Camera captures remain on the client until transformation
- **Secure Transmission**: All API communications use HTTPS in production
- **Privacy First**: No user data collection or tracking

### Camera Security

- **Explicit Permissions**: Camera access requires user consent
- **Stream Management**: Automatic cleanup of camera streams after use
- **Browser Security**: Leverages native browser security for camera access
- **HTTPS Requirement**: Camera functionality requires secure connections in production

## 🔧 Technical Architecture

### Frontend Architecture

```
src/
├── components/          # React components
│   ├── ImageUpload.js   # File upload and camera capture
│   ├── ImagePreview.js  # Image display and preview
│   └── AdvancedSettings.js # Style and parameter controls
├── services/
│   └── api.js          # API communication layer
└── __tests__/          # Component testing suite
```

### Backend Architecture

```
├── app.py              # Flask application entry point
├── config.py           # Configuration management
├── utils.py            # Image processing utilities
├── models/             # AI model storage
└── scripts/            # Utility and management scripts
```

### AI Pipeline

1. **Image Preprocessing**: Resize, normalize, and prepare input
2. **Style Selection**: Load appropriate LoRA model weights
3. **Diffusion Process**: Apply Stable Diffusion with Ukiyo-e styling
4. **Post-processing**: Enhance and finalize the artistic output

## 🌐 Browser Compatibility

| Browser       | Version | Camera Support | WebRTC | Canvas API |
| ------------- | ------- | -------------- | ------ | ---------- |
| Chrome        | 53+     | ✅ Full        | ✅     | ✅         |
| Firefox       | 36+     | ✅ Full        | ✅     | ✅         |
| Safari        | 11+     | ✅ Full        | ✅     | ✅         |
| Edge          | 12+     | ✅ Full        | ✅     | ✅         |
| Mobile Chrome | 53+     | ✅ Full        | ✅     | ✅         |
| Mobile Safari | 11+     | ✅ Full        | ✅     | ✅         |

### Feature Support Notes

- **Camera switching** may be limited on some older mobile devices
- **HTTPS required** for camera access in all modern browsers
- **WebGL support** recommended for optimal performance

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Make** your changes
5. **Test** thoroughly
6. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Submit** a Pull Request

### Code Standards

- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

### Issues and Feature Requests

- Use the issue tracker for bug reports
- Provide detailed reproduction steps
- Include system information and browser details
- Use feature request template for new ideas

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Traditional Ukiyo-e artists who inspired this work
- The Stable Diffusion community for foundational AI models
- Contributors and testers who helped improve the application
- Japanese cultural preservation organizations

## 📞 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Community**: Join discussions in GitHub Discussions
- **Updates**: Watch the repository for latest releases and updates

---

<div align="center">

**[⬆ Back to Top](#-ukiyoefusion)**

Made with ❤️ for art enthusiasts and technology lovers

</div>
