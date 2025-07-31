from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import base64
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
import json
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'])

# Configuration
UPLOAD_FOLDER = 'uploads'
MODELS_FOLDER = 'models'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Global variables for models
current_pipeline = None
current_model = None
available_models = {}

# Predefined Ukiyo-e styles
STYLES = {
    "classic_ukiyo": {
        "name": "Classic Ukiyo-e",
        "prompt": "Authentic Edo-period ukiyo-e woodblock print, flat perspective, bold black outlines, watercolor palette, nature/figures balanced, kabuki influence, masterpiece, by Utamaro/Hokusai/Hiroshige, muted earth tones, matte finish",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast, neon colors, texture, canvas, brush strokes"
    },
    "hokusai_style": {
        "name": "Hokusai Style",
        "prompt": "Hokusai ukiyo-e style, great wave, Mount Fuji, bold blue and white, traditional Japanese woodblock print, flowing water patterns, detailed line work, flat colors",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast, neon colors"
    },
    "hiroshige_landscape": {
        "name": "Hiroshige Landscape",
        "prompt": "Hiroshige landscape ukiyo-e style, scenic views, travel scenes, atmospheric perspective, seasonal changes, traditional Japanese architecture, soft color gradients",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast"
    },
    "utamaro_beauty": {
        "name": "Utamaro Beauty",
        "prompt": "Utamaro bijin-ga style, beautiful women, elegant poses, traditional Japanese clothing, kimono patterns, delicate features, refined composition",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast"
    },
    "kabuki_theatrical": {
        "name": "Kabuki Theatrical",
        "prompt": "Kabuki actor ukiyo-e style, dramatic poses, theatrical makeup, colorful costumes, stage performance, traditional Japanese theater",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast"
    },
    "nature_seasonal": {
        "name": "Seasonal Nature",
        "prompt": "Japanese seasonal ukiyo-e style, cherry blossoms, autumn leaves, snow scenes, traditional garden, natural harmony, seasonal flowers",
        "negative_prompt": "modern, western, 3D, photography, realism, shading, depth of field, anime, manga, CGI, oil painting, sharp details, high contrast"
    }
}

def scan_for_models():
    """Scan for available models - only use Ukiyo-e custom model"""
    global available_models
    
    # Only use the custom Ukiyo-e model
    ukiyo_model_path = os.path.join(MODELS_FOLDER, "ukiyo_e_lora")
    
    available_models = {}
    
    # Check if custom Ukiyo-e model exists
    if os.path.exists(ukiyo_model_path) and os.path.exists(os.path.join(ukiyo_model_path, "model_index.json")):
        available_models["ukiyo_e_lora"] = {
            "name": "Ukiyo-e Traditional Art",
            "type": "local",
            "path": ukiyo_model_path,
            "description": "Authentic Edo-period woodblock print style"
        }
        logger.info(f"Found Ukiyo-e model at: {ukiyo_model_path}")
    else:
        logger.warning(f"Ukiyo-e model not found at: {ukiyo_model_path}")
        # Fallback to online model if custom model not available
        available_models["runwayml/stable-diffusion-v1-5"] = {
            "name": "Stable Diffusion v1.5 (Fallback)",
            "type": "online",
            "path": "runwayml/stable-diffusion-v1-5",
            "description": "Standard model (will be converted to Ukiyo-e style)"
        }
    
    logger.info(f"Available models: {list(available_models.keys())}")
    return available_models

def load_model(model_id):
    """Load a specific model with Ukiyo-e optimizations"""
    global current_pipeline, current_model
    
    if current_model == model_id and current_pipeline is not None:
        return current_pipeline
    
    try:
        model_info = available_models.get(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found")
        
        logger.info(f"Loading model: {model_info['name']}")
        
        # Clear current pipeline to free memory
        if current_pipeline:
            del current_pipeline
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        # Determine device and dtype
        if torch.cuda.is_available():
            device = "cuda"
            torch_dtype = torch.float16
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            torch_dtype = torch.float32
        else:
            device = "cpu"
            torch_dtype = torch.float32
        
        logger.info(f"Using device: {device}")
        
        # Load the pipeline with optimizations
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_info['path'],
            torch_dtype=torch_dtype,
            safety_checker=None,
            requires_safety_checker=False,
            low_cpu_mem_usage=True if device == "cpu" else False
        )
        
        # Use DPM Solver for better quality (as in the custom script)
        from diffusers import DPMSolverMultistepScheduler
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
        
        # Move to device
        pipeline = pipeline.to(device)
        
        # Enable memory efficient optimizations
        if hasattr(pipeline, 'enable_attention_slicing'):
            pipeline.enable_attention_slicing()
        if hasattr(pipeline, 'enable_vae_slicing'):
            pipeline.enable_vae_slicing()
        
        current_pipeline = pipeline
        current_model = model_id
        logger.info(f"Model loaded successfully: {model_info['name']} on {device}")
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Error loading model {model_id}: {str(e)}")
        raise

def process_image(image_data, prompt="", negative_prompt="", style="classic_ukiyo", 
                 strength=0.78, guidance_scale=8.5, num_inference_steps=25, model_id=None):
    """Process image with Ukiyo-e transformation"""
    try:
        # Decode base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Resize image - use 512x512 for optimal Ukiyo-e results
        target_size = 512
        aspect_ratio = image.size[0] / image.size[1]
        
        if aspect_ratio > 1:  # Landscape
            width = target_size
            height = int(target_size / aspect_ratio)
        else:  # Portrait or square
            height = target_size
            width = int(target_size * aspect_ratio)
        
        # Make dimensions divisible by 8
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Load model - default to Ukiyo-e model
        if not model_id:
            model_id = "ukiyo_e_lora" if "ukiyo_e_lora" in available_models else list(available_models.keys())[0]
        
        pipeline = load_model(model_id)
        
        # Get style information
        style_info = STYLES.get(style, STYLES["classic_ukiyo"])
        
        # Build prompts - if user prompt is empty, use only style prompt
        if prompt.strip():
            # Combine user prompt with style
            full_prompt = f"{style_info['prompt']}, {prompt.strip()}"
        else:
            # Use only style prompt for pure Ukiyo-e transformation
            full_prompt = style_info['prompt']
        
        # Always use style negative prompt (don't expose to UI)
        full_negative_prompt = style_info['negative_prompt']
        
        logger.info(f"Processing image with Ukiyo-e style: {style}")
        logger.info(f"Using prompt: {full_prompt}")
        
        # Generate image with Ukiyo-e optimized parameters
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
            result = pipeline(
                prompt=full_prompt,
                image=image,
                strength=strength,
                guidance_scale=guidance_scale,
                negative_prompt=full_negative_prompt,
                num_inference_steps=num_inference_steps,
                width=width,
                height=height
            ).images[0]
        
        # Convert result to base64
        output_buffer = io.BytesIO()
        result.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        result_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return {
            'success': True,
            'image': f"data:image/png;base64,{result_base64}",
            'prompt_used': full_prompt,
            'negative_prompt_used': full_negative_prompt,
            'style_applied': style_info['name'],
            'dimensions': f"{width}x{height}"
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    scan_for_models()
    return jsonify({
        'models': available_models,
        'current_model': current_model
    })

@app.route('/api/styles', methods=['GET'])
def get_styles():
    """Get available styles"""
    return jsonify({'styles': STYLES})

@app.route('/api/transform', methods=['POST'])
def transform_image():
    """Transform an image with Ukiyo-e style"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Extract parameters - make prompt optional
        image_data = data['image']
        prompt = data.get('prompt', '')  # Optional, can be empty
        style = data.get('style', 'classic_ukiyo')  # Default to classic Ukiyo-e
        strength = float(data.get('strength', 0.78))  # Ukiyo-e optimized default
        guidance_scale = float(data.get('guidance_scale', 8.5))  # Ukiyo-e optimized
        num_inference_steps = int(data.get('num_inference_steps', 25))  # Faster for Ukiyo-e
        model_id = data.get('model_id')  # Will default to Ukiyo-e model
        
        # Process the image
        result = process_image(
            image_data=image_data,
            prompt=prompt,  # Can be empty
            style=style,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            model_id=model_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in transform_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cuda_available': torch.cuda.is_available(),
        'current_model': current_model
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'UkiyoeFusion API',
        'version': '1.0.0',
        'endpoints': [
            '/api/models',
            '/api/styles', 
            '/api/transform',
            '/api/health'
        ]
    })

if __name__ == '__main__':
    logger.info("🎨 Starting UkiyoeFusion API Server")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    
    # Scan for available models on startup
    scan_for_models()
    
    # Use port 5001 to avoid conflicts with AirPlay
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
