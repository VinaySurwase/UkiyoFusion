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
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'], 
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

# Predefined Ukiyo-e styles - Multiple authentic styles
STYLES = {
    "classic_ukiyo": {
        "name": "Classic Ukiyo-e",
        "prompt": "ukiyo-e woodblock print, traditional Japanese art, Edo period style, bold black outlines, flat color blocks, no gradients, simplified forms, decorative patterns, traditional pigments, woodcut texture, printmaking style, Japanese aesthetics, stylized composition, geometric shapes, strong contrast, masterpiece",
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, shadows, depth, modern style, western art, photograph, detailed textures, soft edges, blurred lines, contemporary, digital art, airbrushed, smooth surfaces"
    },
    "landscape_ukiyo": {
        "name": "Landscape Ukiyo-e", 
        "prompt": "ukiyo-e landscape print, traditional Japanese scenery, Mount Fuji, cherry blossoms, traditional architecture, bold outlines, flat colors, stylized nature, Edo period landscape art, woodblock print texture, Japanese countryside, serene composition, masterpiece",
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, shadows, modern buildings, western landscape, photograph, detailed textures, contemporary, digital art"
    },
    "portrait_ukiyo": {
        "name": "Portrait Ukiyo-e",
        "prompt": "ukiyo-e portrait print, traditional Japanese figure, geisha, samurai, kabuki actor, elegant kimono patterns, bold facial features, flat color blocks, decorative background, Edo period portraiture, woodblock print style, stylized human figure, masterpiece", 
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, modern clothing, western portrait, photograph, detailed skin texture, contemporary fashion, digital art"
    },
    "nature_ukiyo": {
        "name": "Nature Ukiyo-e",
        "prompt": "ukiyo-e nature print, traditional Japanese flora and fauna, birds, flowers, bamboo, pine trees, decorative natural elements, bold outlines, seasonal themes, woodblock print texture, stylized organic forms, flat color palette, masterpiece",
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, modern nature photography, western botanical art, detailed textures, contemporary, digital art"
    },
    "urban_ukiyo": {
        "name": "Urban Ukiyo-e", 
        "prompt": "ukiyo-e urban scene, traditional Japanese city life, Edo period streets, merchant districts, traditional architecture, busy marketplace, bold outlines, flat colors, stylized urban composition, woodblock print style, cultural scenes, masterpiece",
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, modern city, skyscrapers, cars, contemporary urban life, western architecture, photograph, digital art"
    },
    "seasonal_ukiyo": {
        "name": "Seasonal Ukiyo-e",
        "prompt": "ukiyo-e seasonal print, traditional Japanese seasons, spring cherry blossoms, summer festivals, autumn maple leaves, winter snow scenes, seasonal activities, bold outlines, flat colors, decorative seasonal elements, woodblock print texture, masterpiece",
        "negative_prompt": "photorealistic, realistic, 3D render, gradients, shading, modern seasonal scenes, western seasonal art, photograph, detailed textures, contemporary, digital art"
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
        
        # Load the standard pipeline
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_info['path'],
            torch_dtype=torch_dtype,
            safety_checker=None,
            requires_safety_checker=False,
            low_cpu_mem_usage=True if device == "cpu" else False
        )
        
        # Use DPM Solver for better quality
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
                 strength=0.85, guidance_scale=12.0, num_inference_steps=30, model_id=None):
    """Process image with Ukiyo-e transformation"""
    try:
        # Decode base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Resize image - use fixed 512x512 dimensions
        width = 512
        height = 512
        
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Load model - default to Ukiyo-e model
        if not model_id:
            model_id = "ukiyo_e_lora" if "ukiyo_e_lora" in available_models else list(available_models.keys())[0]
        
        pipeline = load_model(model_id)
        
        # Get style information
        style_info = STYLES.get(style, STYLES["classic_ukiyo"])
        
        # Build prompts - if user prompt is provided, append it to the default prompt
        if prompt.strip():
            # Append user prompt to the default style prompt
            full_prompt = f"{style_info['prompt']}, {prompt.strip()}"
        else:
            # Use only the default style prompt
            full_prompt = style_info['prompt']
        
        # Always use style negative prompt
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

# API Routes
@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    return jsonify({'models': available_models})

@app.route('/api/styles', methods=['GET'])
def get_styles():
    """Get available styles"""
    return jsonify({'styles': STYLES})

@app.route('/api/controlnet', methods=['GET'])
def get_controlnet_options():
    """Get available ControlNet options - returns empty for fallback version"""
    return jsonify({'controlnet_options': {}})

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
        strength = float(data.get('strength', 0.85))  # Higher for more style transformation
        guidance_scale = float(data.get('guidance_scale', 12.0))  # Higher for stronger style adherence
        num_inference_steps = int(data.get('num_inference_steps', 30))  # More steps for better quality
        model_id = data.get('model_id')  # Will default to Ukiyo-e model
        
        # Process the image
        result = process_image(
            image_data=image_data,
            prompt=prompt,
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
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return jsonify({
        'message': 'UkiyoeFusion API (Fallback Version)',
        'version': '1.0.0',
        'endpoints': [
            '/api/models',
            '/api/styles', 
            '/api/controlnet',
            '/api/transform',
            '/api/health'
        ]
    })

if __name__ == '__main__':
    logger.info("🎨 Starting UkiyoeFusion API Server (Fallback Version)")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    
    # Scan for available models on startup
    scan_for_models()
    
    # Use port 5001 to avoid conflicts with AirPlay
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
