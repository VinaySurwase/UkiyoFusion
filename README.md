# UkiyoeFusion - Traditional Japanese Art Transformation

Transform any image into authentic Ukiyo-e (traditional Japanese woodblock print) style using AI.

## Features

- **Authentic Ukiyo-e Transformation**: Custom-trained model for traditional Japanese art style
- **Multiple Ukiyo-e Styles**: Classic, Hokusai, Hiroshige, Utamaro, Kabuki, and Seasonal styles
- **Multiple Input Methods**: Upload files, drag & drop, or capture photos directly from camera
- **Camera Integration**: Take photos directly in the app with front/back camera switching
- **Optional Prompts**: Works beautifully with or without additional descriptions
- **Optimized Parameters**: Pre-configured for best Ukiyo-e results
- **Simple Interface**: Clean, focused interface without unnecessary complexity

## Tech Stack

- **Backend**: Flask, Diffusers, PyTorch
- **Frontend**: React, Material-UI
- **AI Models**: Stable Diffusion, Custom Models

## Quick Start

```bash
# Make the run script executable and start everything
chmod +x run.sh
./run.sh
```

## Manual Setup

1. Install Python dependencies: `pip install -r requirements.txt`
2. Install Node.js dependencies: `cd frontend && npm install`
3. Start backend: `python app.py`
4. Start frontend: `cd frontend && npm start`

## Adding Custom Models

Place your custom model files in the `models/` directory and they will be automatically detected.

## API Endpoints

- `POST /api/transform` - Transform image
- `GET /api/models` - List available models
- `GET /api/styles` - List available styles
