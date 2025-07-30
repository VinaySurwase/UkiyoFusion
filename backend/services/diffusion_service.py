import torch
import os
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionControlNetImg2ImgPipeline
from diffusers import ControlNetModel, DPMSolverMultistepScheduler
from controlnet_aux import CannyDetector, LineartDetector, OpenposeDetector
from transformers import pipeline
from PIL import Image
import numpy as np
import structlog
from typing import Dict, List, Optional, Tuple
import gc

logger = structlog.get_logger()

class DiffusionService:
    """Service for handling diffusion model operations"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.models = {}
        self.controlnets = {}
        self.preprocessors = {}
        
        # Available models configuration
        self.available_models = {
            'stable-diffusion-v1-5': {
                'name': 'stable-diffusion-v1-5',
                'display_name': 'Stable Diffusion v1.5',
                'description': 'General purpose image-to-image transformation',
                'model_id': 'runwayml/stable-diffusion-v1-5',
                'type': 'stable-diffusion',
                'is_premium': False
            },
            'stable-diffusion-xl': {
                'name': 'stable-diffusion-xl',
                'display_name': 'Stable Diffusion XL',
                'description': 'High-resolution image generation with better quality',
                'model_id': 'stabilityai/stable-diffusion-xl-base-1.0',
                'type': 'stable-diffusion-xl',
                'is_premium': True
            },
            'ukiyo-e-diffusion': {
                'name': 'ukiyo-e-diffusion',
                'display_name': 'Ukiyo-e Style Transfer',
                'description': 'Specialized model for Japanese woodblock print style',
                'model_id': 'sd-dreambooth-library/ukiyoe-style',
                'type': 'stable-diffusion',
                'is_premium': False
            }
        }
        
        logger.info("DiffusionService initialized", device=self.device, dtype=str(self.dtype))
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        return list(self.available_models.values())
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model into memory"""
        try:
            if model_name in self.models:
                logger.info("Model already loaded", model_name=model_name)
                return True
            
            if model_name not in self.available_models:
                logger.error("Model not available", model_name=model_name)
                return False
            
            model_config = self.available_models[model_name]
            model_id = model_config['model_id']
            
            logger.info("Loading model", model_name=model_name, model_id=model_id)
            
            # Load model based on type
            if model_config['type'] == 'stable-diffusion':
                pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                    model_id,
                    torch_dtype=self.dtype,
                    safety_checker=None,
                    requires_safety_checker=False,
                    use_safetensors=True,
                    cache_dir=os.getenv('MODEL_CACHE_DIR', './models')
                )
            elif model_config['type'] == 'stable-diffusion-xl':
                pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                    model_id,
                    torch_dtype=self.dtype,
                    use_safetensors=True,
                    variant="fp16",
                    cache_dir=os.getenv('MODEL_CACHE_DIR', './models')
                )
            else:
                logger.error("Unsupported model type", model_type=model_config['type'])
                return False
            
            # Optimize pipeline
            pipeline = pipeline.to(self.device)
            pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
            
            # Enable memory efficient attention if available
            if hasattr(pipeline, "enable_xformers_memory_efficient_attention"):
                try:
                    pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("XFormers memory efficient attention enabled")
                except Exception as e:
                    logger.warning("Failed to enable XFormers", error=str(e))
            
            # Enable CPU offload for better memory management
            if self.device == "cuda":
                pipeline.enable_model_cpu_offload()
                pipeline.enable_vae_slicing()
                pipeline.enable_vae_tiling()
            
            self.models[model_name] = pipeline
            logger.info("Model loaded successfully", model_name=model_name)
            return True
            
        except Exception as e:
            logger.error("Failed to load model", model_name=model_name, error=str(e))
            return False
    
    def load_controlnet(self, controlnet_type: str) -> bool:
        """Load ControlNet model"""
        try:
            if controlnet_type in self.controlnets:
                return True
            
            controlnet_models = {
                'canny': 'lllyasviel/sd-controlnet-canny',
                'depth': 'lllyasviel/sd-controlnet-depth',
                'openpose': 'lllyasviel/sd-controlnet-openpose',
                'lineart': 'lllyasviel/sd-controlnet-mlsd'
            }
            
            if controlnet_type not in controlnet_models:
                return False
            
            logger.info("Loading ControlNet", type=controlnet_type)
            
            controlnet = ControlNetModel.from_pretrained(
                controlnet_models[controlnet_type],
                torch_dtype=self.dtype,
                cache_dir=os.getenv('MODEL_CACHE_DIR', './models')
            )
            
            self.controlnets[controlnet_type] = controlnet
            
            # Load preprocessor
            if controlnet_type == 'canny':
                self.preprocessors[controlnet_type] = CannyDetector()
            elif controlnet_type == 'openpose':
                self.preprocessors[controlnet_type] = OpenposeDetector.from_pretrained('lllyasviel/Annotators')
            elif controlnet_type == 'lineart':
                self.preprocessors[controlnet_type] = LineartDetector.from_pretrained('lllyasviel/Annotators')
            
            logger.info("ControlNet loaded successfully", type=controlnet_type)
            return True
            
        except Exception as e:
            logger.error("Failed to load ControlNet", type=controlnet_type, error=str(e))
            return False
    
    def preprocess_image(self, image: Image.Image, max_size: int = 1024) -> Image.Image:
        """Preprocess input image"""
        # Resize image while maintaining aspect ratio
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Ensure dimensions are multiples of 8 (required by diffusion models)
        width, height = image.size
        width = (width // 8) * 8
        height = (height // 8) * 8
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def generate_image(
        self,
        image: Image.Image,
        prompt: str,
        model_name: str = 'stable-diffusion-v1-5',
        negative_prompt: str = "",
        strength: float = 0.8,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 20,
        seed: Optional[int] = None,
        controlnet_type: Optional[str] = None
    ) -> Optional[Image.Image]:
        """Generate transformed image"""
        try:
            # Load model if not already loaded
            if not self.load_model(model_name):
                return None
            
            pipeline = self.models[model_name]
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Set random seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                if self.device == "cuda":
                    torch.cuda.manual_seed(seed)
            
            # Prepare generation arguments
            generation_args = {
                'image': processed_image,
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'strength': strength,
                'guidance_scale': guidance_scale,
                'num_inference_steps': num_inference_steps,
                'generator': torch.Generator(device=self.device).manual_seed(seed) if seed else None
            }
            
            # Use ControlNet if specified
            if controlnet_type and self.load_controlnet(controlnet_type):
                controlnet = self.controlnets[controlnet_type]
                preprocessor = self.preprocessors.get(controlnet_type)
                
                if preprocessor:
                    # Preprocess image for ControlNet
                    if controlnet_type == 'canny':
                        control_image = preprocessor(processed_image)
                    else:
                        control_image = preprocessor(processed_image)
                    
                    # Create ControlNet pipeline
                    controlnet_pipeline = StableDiffusionControlNetImg2ImgPipeline(
                        vae=pipeline.vae,
                        text_encoder=pipeline.text_encoder,
                        tokenizer=pipeline.tokenizer,
                        unet=pipeline.unet,
                        controlnet=controlnet,
                        scheduler=pipeline.scheduler,
                        safety_checker=pipeline.safety_checker,
                        feature_extractor=pipeline.feature_extractor,
                    ).to(self.device)
                    
                    generation_args['control_image'] = control_image
                    result = controlnet_pipeline(**generation_args)
                else:
                    result = pipeline(**generation_args)
            else:
                result = pipeline(**generation_args)
            
            # Clean up GPU memory
            if self.device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            
            return result.images[0]
            
        except Exception as e:
            logger.error("Image generation failed", error=str(e))
            # Clean up GPU memory on error
            if self.device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            return None
    
    def unload_model(self, model_name: str):
        """Unload model from memory"""
        if model_name in self.models:
            del self.models[model_name]
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            logger.info("Model unloaded", model_name=model_name)
    
    def get_memory_usage(self) -> Dict:
        """Get current memory usage"""
        memory_info = {}
        
        if self.device == "cuda" and torch.cuda.is_available():
            memory_info['gpu_allocated'] = torch.cuda.memory_allocated()
            memory_info['gpu_reserved'] = torch.cuda.memory_reserved()
            memory_info['gpu_max_allocated'] = torch.cuda.max_memory_allocated()
        
        import psutil
        process = psutil.Process()
        memory_info['cpu_memory'] = process.memory_info().rss
        
        return memory_info
    
    def clear_cache(self):
        """Clear all cached models and free memory"""
        self.models.clear()
        self.controlnets.clear()
        self.preprocessors.clear()
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
        
        logger.info("Cache cleared")

# Global service instance
diffusion_service = DiffusionService()
