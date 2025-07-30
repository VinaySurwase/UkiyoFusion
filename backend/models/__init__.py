import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(128))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Usage tracking
    total_transformations = db.Column(db.Integer, default=0)
    storage_used = db.Column(db.BigInteger, default=0)  # in bytes
    
    # Relationships
    transformations = db.relationship('Transformation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    gallery_items = db.relationship('GalleryItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': str(self.id),
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_transformations': self.total_transformations,
            'storage_used': self.storage_used
        }
        return {k: v for k, v in data.items() if v is not None}
    
    def __repr__(self):
        return f'<User {self.username}>'


class Transformation(db.Model):
    """Model for image transformation requests and results"""
    __tablename__ = 'transformations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Task information
    task_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='transformation_status'), 
                      default='pending', index=True)
    
    # Input data
    original_filename = db.Column(db.String(255), nullable=False)
    original_url = db.Column(db.String(512), nullable=False)
    original_size = db.Column(db.BigInteger)  # file size in bytes
    
    # Transformation parameters
    model_name = db.Column(db.String(128), nullable=False)
    prompt = db.Column(db.Text)
    negative_prompt = db.Column(db.Text)
    strength = db.Column(db.Float, default=0.8)
    guidance_scale = db.Column(db.Float, default=7.5)
    num_inference_steps = db.Column(db.Integer, default=20)
    seed = db.Column(db.BigInteger)
    
    # Output data
    result_filename = db.Column(db.String(255))
    result_url = db.Column(db.String(512))
    result_size = db.Column(db.BigInteger)
    
    # Processing info
    processing_time = db.Column(db.Float)  # in seconds
    gpu_memory_used = db.Column(db.BigInteger)  # in bytes
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    gallery_items = db.relationship('GalleryItem', backref='transformation', lazy='dynamic')
    
    def to_dict(self):
        """Convert transformation to dictionary"""
        return {
            'id': str(self.id),
            'task_id': self.task_id,
            'status': self.status,
            'original_filename': self.original_filename,
            'original_url': self.original_url,
            'original_size': self.original_size,
            'model_name': self.model_name,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'strength': self.strength,
            'guidance_scale': self.guidance_scale,
            'num_inference_steps': self.num_inference_steps,
            'seed': self.seed,
            'result_filename': self.result_filename,
            'result_url': self.result_url,
            'result_size': self.result_size,
            'processing_time': self.processing_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Transformation {self.task_id}>'


class GalleryItem(db.Model):
    """Model for user's gallery items"""
    __tablename__ = 'gallery_items'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    transformation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('transformations.id'), nullable=False)
    
    # Gallery item info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))  # comma-separated tags
    
    # Visibility and sharing
    is_public = db.Column(db.Boolean, default=False, index=True)
    is_featured = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(128), unique=True, index=True)
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_share_token(self):
        """Generate unique share token"""
        import secrets
        self.share_token = secrets.token_urlsafe(32)
    
    def to_dict(self, include_transformation=True):
        """Convert gallery item to dictionary"""
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'tags': self.tags.split(',') if self.tags else [],
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'share_token': self.share_token,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_transformation and self.transformation:
            data['transformation'] = self.transformation.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<GalleryItem {self.title}>'


class ModelConfig(db.Model):
    """Model configuration and metadata"""
    __tablename__ = 'model_configs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(128), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Model details
    model_type = db.Column(db.String(50), nullable=False)  # 'stable-diffusion', 'controlnet', etc.
    huggingface_id = db.Column(db.String(200))
    local_path = db.Column(db.String(500))
    
    # Configuration
    default_prompt = db.Column(db.Text)
    default_negative_prompt = db.Column(db.Text)
    max_image_size = db.Column(db.Integer, default=1024)
    supported_formats = db.Column(db.String(100), default='jpg,png,webp')
    
    # Status and metrics
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_premium = db.Column(db.Boolean, default=False)
    avg_processing_time = db.Column(db.Float)  # in seconds
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model config to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'model_type': self.model_type,
            'default_prompt': self.default_prompt,
            'default_negative_prompt': self.default_negative_prompt,
            'max_image_size': self.max_image_size,
            'supported_formats': self.supported_formats.split(',') if self.supported_formats else [],
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'avg_processing_time': self.avg_processing_time,
            'usage_count': self.usage_count
        }
    
    def __repr__(self):
        return f'<ModelConfig {self.name}>'
