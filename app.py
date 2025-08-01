from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import base64
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel
import json
from datetime import datetime
import uuid
import logging
import cv2
import numpy as np
from controlnet_aux import CannyDetector, MidasDetector, OpenposeDetector

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

# ControlNet models for structural guidance
controlnet_models = {}
controlnet_processors = {}

# ControlNet configurations for different guidance types
CONTROLNET_CONFIGS = {
    "canny": {
        "model_id": "lllyasviel/sd-controlnet-canny",
        "name": "Canny Edge Detection",
        "description": "Preserves edge structure and outlines"
    },
    "depth": {
        "model_id": "lllyasviel/sd-controlnet-depth", 
        "name": "Depth Estimation",
        "description": "Maintains depth and spatial relationships"
    },
    "openpose": {
        "model_id": "lllyasviel/sd-controlnet-openpose",
        "name": "Pose Detection", 
        "description": "Preserves human pose and body structure"
    }
}

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

def initialize_controlnet_models():
    """Initialize ControlNet models and processors"""
    global controlnet_models, controlnet_processors
    
    try:
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            torch_dtype = torch.float16
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            torch_dtype = torch.float32
        else:
            device = "cpu"
            torch_dtype = torch.float32
            
        logger.info(f"Initializing ControlNet models on device: {device}")
        
        # Initialize ControlNet models
        for control_type, config in CONTROLNET_CONFIGS.items():
            try:
                logger.info(f"Loading ControlNet model: {config['name']}")
                controlnet = ControlNetModel.from_pretrained(
                    config['model_id'],
                    torch_dtype=torch_dtype
                ).to(device)
                controlnet_models[control_type] = controlnet
                logger.info(f"✓ Loaded {config['name']} ControlNet")
            except Exception as e:
                logger.warning(f"Failed to load {config['name']} ControlNet: {str(e)}")
        
        # Initialize preprocessors
        try:
            controlnet_processors['canny'] = CannyDetector()
            logger.info("✓ Initialized Canny detector")
        except Exception as e:
            logger.warning(f"Failed to initialize Canny detector: {str(e)}")
            
        try:
            controlnet_processors['depth'] = MidasDetector.from_pretrained('valhalla/t2iadapter-aux-models')
            logger.info("✓ Initialized Depth detector")
        except Exception as e:
            logger.warning(f"Failed to initialize Depth detector: {str(e)}")
            
        try:
            controlnet_processors['openpose'] = OpenposeDetector.from_pretrained('valhalla/t2iadapter-aux-models')
            logger.info("✓ Initialized Pose detector")
        except Exception as e:
            logger.warning(f"Failed to initialize Pose detector: {str(e)}")
            
        logger.info(f"ControlNet initialization complete. Available: {list(controlnet_models.keys())}")
        
    except Exception as e:
        logger.error(f"Error initializing ControlNet models: {str(e)}")

def preprocess_controlnet_input(image, control_type, **kwargs):
    """Preprocess image for specific ControlNet type"""
    try:
        if control_type == 'canny':
            low_threshold = kwargs.get('low_threshold', 100)
            high_threshold = kwargs.get('high_threshold', 200)
            control_image = controlnet_processors['canny'](
                image, 
                low_threshold=low_threshold, 
                high_threshold=high_threshold
            )
            
        elif control_type == 'depth':
            control_image = controlnet_processors['depth'](image)
            
        elif control_type == 'openpose':
            control_image = controlnet_processors['openpose'](image)
            
        else:
            raise ValueError(f"Unsupported ControlNet type: {control_type}")
            
        return control_image
        
    except Exception as e:
        logger.error(f"Error preprocessing image for {control_type}: {str(e)}")
        raise

def load_model(model_id, control_type=None):
    """Load a specific model with Ukiyo-e optimizations and optional ControlNet"""
    global current_pipeline, current_model
    
    # Create a unique identifier for the pipeline configuration
    pipeline_id = f"{model_id}_{control_type}" if control_type else model_id
    
    if current_model == pipeline_id and current_pipeline is not None:
        return current_pipeline
    
    try:
        model_info = available_models.get(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found")
        
        logger.info(f"Loading model: {model_info['name']} with ControlNet: {control_type or 'None'}")
        
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
        
        # Load the pipeline with ControlNet if specified
        if control_type and control_type in controlnet_models:
            # Load ControlNet pipeline
            controlnet = controlnet_models[control_type]
            pipeline = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                model_info['path'],
                controlnet=controlnet,
                torch_dtype=torch_dtype,
                safety_checker=None,
                requires_safety_checker=False,
                low_cpu_mem_usage=True if device == "cpu" else False
            )
            logger.info(f"Loaded ControlNet pipeline with {CONTROLNET_CONFIGS[control_type]['name']}")
        else:
            # Load standard pipeline
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
        current_model = pipeline_id
        logger.info(f"Model loaded successfully: {model_info['name']} on {device}")
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Error loading model {model_id}: {str(e)}")
        raise

def process_image(image_data, prompt="", negative_prompt="", style="classic_ukiyo", 
                 strength=0.85, guidance_scale=12.0, num_inference_steps=30, model_id=None):
    """Process image with Ukiyo-e transformation and automatic ControlNet guidance"""
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
        
        # Automatically determine best ControlNet type
        control_type = "canny"  # Default to canny for edge preservation
        controlnet_conditioning_scale = 0.6  # Lower for more artistic freedom
        
        # Load model - default to Ukiyo-e model
        if not model_id:
            model_id = "ukiyo_e_lora" if "ukiyo_e_lora" in available_models else list(available_models.keys())[0]
        
        # Load pipeline with automatic ControlNet
        pipeline = load_model(model_id, control_type)
        
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
        logger.info(f"Auto-applying ControlNet: {CONTROLNET_CONFIGS[control_type]['name']}")
        
        # Prepare generation parameters
        generation_kwargs = {
            "prompt": full_prompt,
            "image": image,
            "strength": strength,
            "guidance_scale": guidance_scale,
            "negative_prompt": full_negative_prompt,
            "num_inference_steps": num_inference_steps,
            "width": width,
            "height": height
        }
        
        # Add ControlNet parameters automatically
        if control_type and control_type in controlnet_models:
            # Preprocess image for ControlNet
            control_image = preprocess_controlnet_input(
                image, 
                control_type,
                low_threshold=100,
                high_threshold=200
            )
            
            generation_kwargs.update({
                "control_image": control_image,
                "controlnet_conditioning_scale": controlnet_conditioning_scale
            })
            
            logger.info(f"Applied automatic ControlNet guidance with strength {controlnet_conditioning_scale}")
        
        # Generate image with Ukiyo-e optimized parameters
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
            result = pipeline(**generation_kwargs).images[0]
        
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
            'controlnet_used': CONTROLNET_CONFIGS[control_type]['name'] if control_type else None,
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

@app.route('/api/controlnet', methods=['GET'])
def get_controlnet_options():
    """Get available ControlNet options"""
    available_controlnets = {}
    for control_type, config in CONTROLNET_CONFIGS.items():
        if control_type in controlnet_models:
            available_controlnets[control_type] = {
                "name": config["name"],
                "description": config["description"],
                "available": True
            }
        else:
            available_controlnets[control_type] = {
                "name": config["name"], 
                "description": config["description"],
                "available": False
            }
    
    return jsonify({'controlnet_options': available_controlnets})

@app.route('/api/transform', methods=['POST'])
def transform_image():
    """Transform an image with Ukiyo-e style and automatic ControlNet guidance"""
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
        
        # Process the image with automatic ControlNet
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
            '/api/controlnet',
            '/api/transform',
            '/api/health'
        ]
    })

if __name__ == '__main__':
    logger.info("🎨 Starting UkiyoeFusion API Server")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    
    # Scan for available models on startup
    scan_for_models()
    
    # Initialize ControlNet models and processors
    initialize_controlnet_models()
    
    # Use port 5001 to avoid conflicts with AirPlay
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
