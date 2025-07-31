#!/usr/bin/env python3
"""Test script to verify Ukiyo-e model loading"""

import os
import sys
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test if the Ukiyo-e model can be loaded properly"""
    try:
        model_path = "models/ukiyo_e_lora"
        
        print(f"Testing model at: {model_path}")
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"❌ Model path does not exist: {model_path}")
            return False
            
        if not os.path.exists(os.path.join(model_path, "model_index.json")):
            print(f"❌ model_index.json not found in {model_path}")
            return False
            
        print("✅ Model files exist")
        
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            torch_dtype = torch.float16
            print("🚀 Using CUDA")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            torch_dtype = torch.float32
            print("🍎 Using MPS (Apple Silicon)")
        else:
            device = "cpu"
            torch_dtype = torch.float32
            print("💻 Using CPU")
        
        print(f"Device: {device}, dtype: {torch_dtype}")
        
        # Try to load the pipeline
        print("Loading StableDiffusionImg2ImgPipeline...")
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_path,
            torch_dtype=torch_dtype,
            safety_checker=None,
            requires_safety_checker=False,
            low_cpu_mem_usage=True if device == "cpu" else False
        )
        
        print("✅ Pipeline loaded successfully")
        
        # Try to set up DPM Solver
        print("Setting up DPMSolverMultistepScheduler...")
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
        print("✅ Scheduler configured")
        
        # Move to device
        print(f"Moving pipeline to {device}...")
        pipeline = pipeline.to(device)
        print("✅ Pipeline moved to device")
        
        # Enable optimizations
        if hasattr(pipeline, 'enable_attention_slicing'):
            pipeline.enable_attention_slicing()
            print("✅ Attention slicing enabled")
            
        if hasattr(pipeline, 'enable_vae_slicing'):
            pipeline.enable_vae_slicing()
            print("✅ VAE slicing enabled")
        
        print("🎉 Model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎨 UkiyoeFusion Model Test")
    print("=" * 50)
    
    success = test_model_loading()
    
    if success:
        print("\n✅ Model test passed!")
    else:
        print("\n❌ Model test failed!")
        sys.exit(1)
