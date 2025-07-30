import os
from PIL import Image
from werkzeug.datastructures import FileStorage
from typing import Tuple, Optional
import structlog

logger = structlog.get_logger()

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    if not filename:
        return False
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_image(file: FileStorage) -> Tuple[bool, str]:
    """Validate uploaded image file"""
    try:
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
        if file_size > max_size:
            return False, f"File size too large. Maximum size is {max_size // (1024*1024)}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Try to open and validate the image
        try:
            image = Image.open(file)
            image.verify()  # Verify that it's a valid image
            file.seek(0)  # Reset file pointer
            
            # Re-open for dimension check (verify() closes the image)
            image = Image.open(file)
            width, height = image.size
            
            # Check minimum dimensions
            min_size = 64
            if width < min_size or height < min_size:
                return False, f"Image too small. Minimum size is {min_size}x{min_size}px"
            
            # Check maximum dimensions
            max_image_size = int(os.getenv('MAX_IMAGE_SIZE', 2048))
            if width > max_image_size or height > max_image_size:
                return False, f"Image too large. Maximum size is {max_image_size}x{max_image_size}px"
            
            # Check aspect ratio (prevent extremely wide/tall images)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 4.0:
                return False, "Image aspect ratio too extreme. Maximum ratio is 4:1"
            
            file.seek(0)  # Reset file pointer
            return True, "Valid image"
            
        except Exception as e:
            logger.error("Image validation error", error=str(e))
            return False, "Invalid image file or corrupted data"
    
    except Exception as e:
        logger.error("File validation error", error=str(e))
        return False, "File validation failed"

def validate_prompt(prompt: str, max_length: int = 1000) -> Tuple[bool, str]:
    """Validate image generation prompt"""
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    
    prompt = prompt.strip()
    
    if len(prompt) > max_length:
        return False, f"Prompt too long. Maximum length is {max_length} characters"
    
    # Check for potentially harmful content (basic filtering)
    banned_words = [
        'nude', 'naked', 'nsfw', 'porn', 'explicit', 'sexual',
        'violence', 'gore', 'blood', 'death', 'kill', 'murder',
        'hate', 'racist', 'nazi', 'terrorist'
    ]
    
    prompt_lower = prompt.lower()
    for word in banned_words:
        if word in prompt_lower:
            return False, f"Prompt contains inappropriate content: '{word}'"
    
    return True, "Valid prompt"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    
    # Keep only alphanumeric characters, dots, hyphens, and underscores
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple consecutive underscores/dots
    filename = re.sub(r'[_\.]{2,}', '_', filename)
    
    # Ensure filename is not too long
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    
    return name + ext

def get_image_info(image: Image.Image) -> dict:
    """Get comprehensive image information"""
    return {
        'format': image.format,
        'mode': image.mode,
        'size': image.size,
        'width': image.width,
        'height': image.height,
        'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
    }

def resize_image(image: Image.Image, max_size: int = 1024, maintain_aspect: bool = True) -> Image.Image:
    """Resize image while maintaining quality"""
    if maintain_aspect:
        # Resize maintaining aspect ratio
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Ensure dimensions are multiples of 8 (required by diffusion models)
        width, height = image.size
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        if width > 0 and height > 0:
            image = image.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # Resize to exact dimensions
        max_size = (max_size // 8) * 8  # Ensure multiple of 8
        image = image.resize((max_size, max_size), Image.Resampling.LANCZOS)
    
    return image

def optimize_image(image: Image.Image, format: str = 'JPEG', quality: int = 95) -> Image.Image:
    """Optimize image for web delivery"""
    # Convert to RGB if necessary for JPEG
    if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
        # Create white background for transparency
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    
    return image

def calculate_processing_cost(
    width: int, 
    height: int, 
    num_inference_steps: int, 
    model_complexity: float = 1.0
) -> float:
    """Calculate estimated processing cost/time"""
    # Base cost calculation (arbitrary units)
    pixel_count = width * height
    base_cost = (pixel_count / (512 * 512)) * num_inference_steps * model_complexity
    
    return round(base_cost, 2)

def generate_cache_key(
    prompt: str,
    negative_prompt: str,
    model_name: str,
    strength: float,
    guidance_scale: float,
    num_inference_steps: int,
    seed: Optional[int],
    image_hash: str
) -> str:
    """Generate cache key for result caching"""
    import hashlib
    
    cache_data = f"{prompt}|{negative_prompt}|{model_name}|{strength}|{guidance_scale}|{num_inference_steps}|{seed}|{image_hash}"
    return hashlib.sha256(cache_data.encode()).hexdigest()

def get_image_hash(image: Image.Image) -> str:
    """Get hash of image for caching purposes"""
    import hashlib
    import io
    
    # Convert image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Calculate hash
    return hashlib.md5(img_bytes.getvalue()).hexdigest()

def validate_generation_parameters(
    strength: float,
    guidance_scale: float,
    num_inference_steps: int,
    seed: Optional[int] = None
) -> Tuple[bool, str]:
    """Validate image generation parameters"""
    # Validate strength
    if not 0.1 <= strength <= 1.0:
        return False, "Strength must be between 0.1 and 1.0"
    
    # Validate guidance scale
    if not 1.0 <= guidance_scale <= 20.0:
        return False, "Guidance scale must be between 1.0 and 20.0"
    
    # Validate inference steps
    if not 10 <= num_inference_steps <= 100:
        return False, "Number of inference steps must be between 10 and 100"
    
    # Validate seed
    if seed is not None:
        if not isinstance(seed, int) or seed < 0 or seed > 2**32 - 1:
            return False, "Seed must be a positive integer less than 2^32"
    
    return True, "Valid parameters"
