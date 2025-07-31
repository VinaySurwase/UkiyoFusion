"""
Utility functions for UkiyoeFusion
"""

import os
import io
import base64
from PIL import Image
import torch
import logging

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ukiyoe_fusion.log'),
            logging.StreamHandler()
        ]
    )

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['uploads', 'models', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")

def validate_image(image_data):
    """Validate uploaded image data"""
    try:
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Validate format
        if image.format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP']:
            raise ValueError(f"Unsupported image format: {image.format}")
        
        # Validate size
        if max(image.size) > 2048:
            raise ValueError("Image too large. Maximum size is 2048x2048 pixels")
        
        return True, image
        
    except Exception as e:
        return False, str(e)

def optimize_image(image, max_size=768):
    """Optimize image for processing"""
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize if too large
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Make dimensions divisible by 8 (required by Stable Diffusion)
    width = (image.size[0] // 8) * 8
    height = (image.size[1] // 8) * 8
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    return image

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def check_gpu_memory():
    """Check available GPU memory"""
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        for i in range(device_count):
            memory_allocated = torch.cuda.memory_allocated(i)
            memory_cached = torch.cuda.memory_reserved(i)
            total_memory = torch.cuda.get_device_properties(i).total_memory
            
            logger.info(f"GPU {i}: {memory_allocated / 1024**3:.2f}GB allocated, "
                       f"{memory_cached / 1024**3:.2f}GB cached, "
                       f"{total_memory / 1024**3:.2f}GB total")
    else:
        logger.info("No GPU available")

def clear_gpu_cache():
    """Clear GPU cache to free memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("GPU cache cleared")

def validate_prompt(prompt):
    """Validate and clean prompt text"""
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    
    # Remove excessive whitespace
    prompt = ' '.join(prompt.split())
    
    # Check length
    if len(prompt) > 500:
        return False, "Prompt too long. Maximum 500 characters"
    
    return True, prompt

def get_model_info(model_path):
    """Get information about a model"""
    try:
        if os.path.isdir(model_path):
            # Local model
            config_path = os.path.join(model_path, "model_index.json")
            if os.path.exists(config_path):
                return {
                    'type': 'local',
                    'path': model_path,
                    'valid': True
                }
        else:
            # Online model - assume valid if it's a string
            return {
                'type': 'online',
                'path': model_path,
                'valid': True
            }
    except Exception as e:
        logger.error(f"Error checking model {model_path}: {e}")
    
    return {
        'type': 'unknown',
        'path': model_path,
        'valid': False
    }
