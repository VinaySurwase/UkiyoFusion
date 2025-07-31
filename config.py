"""
Configuration file for UkiyoeFusion
"""

import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ukiyoe-fusion-secret-key'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Model settings
    MODELS_FOLDER = 'models'
    DEFAULT_MODEL = 'runwayml/stable-diffusion-v1-5'
    
    # Image processing settings
    MAX_IMAGE_SIZE = 768
    DEFAULT_STEPS = 50
    DEFAULT_GUIDANCE_SCALE = 7.5
    DEFAULT_STRENGTH = 0.75
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # GPU settings
    USE_GPU = True
    GPU_MEMORY_FRACTION = 0.8
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
