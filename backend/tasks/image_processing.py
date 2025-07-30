from celery import current_task
from datetime import datetime
import io
import uuid
from PIL import Image
import structlog

from models import db, Transformation, User
from services.diffusion_service import diffusion_service
from services.storage_service import storage_service
from utils.validators import validate_prompt, validate_generation_parameters

logger = structlog.get_logger()

def process_image_task(
    task_id: str,
    user_id: str,
    image_data: bytes,
    filename: str,
    model_name: str,
    prompt: str,
    negative_prompt: str = "",
    strength: float = 0.8,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 20,
    seed: int = None
):
    """Celery task for processing image transformation"""
    
    try:
        # Update task status to processing
        transformation = Transformation.query.filter_by(task_id=task_id).first()
        if not transformation:
            logger.error("Transformation not found", task_id=task_id)
            return {'status': 'failed', 'error': 'Transformation not found'}
        
        transformation.status = 'processing'
        transformation.started_at = datetime.utcnow()
        db.session.commit()
        
        # Emit progress update via WebSocket
        emit_progress_update(task_id, 'processing', 'Starting image transformation...', 10)
        
        # Validate prompt
        is_valid_prompt, prompt_error = validate_prompt(prompt)
        if not is_valid_prompt:
            raise ValueError(f"Invalid prompt: {prompt_error}")
        
        # Validate generation parameters
        is_valid_params, params_error = validate_generation_parameters(
            strength, guidance_scale, num_inference_steps, seed
        )
        if not is_valid_params:
            raise ValueError(f"Invalid parameters: {params_error}")
        
        emit_progress_update(task_id, 'processing', 'Loading AI model...', 20)
        
        # Load the model
        if not diffusion_service.load_model(model_name):
            raise RuntimeError(f"Failed to load model: {model_name}")
        
        emit_progress_update(task_id, 'processing', 'Preprocessing image...', 30)
        
        # Load and preprocess image
        image = Image.open(io.BytesIO(image_data))
        
        # Get initial memory usage
        memory_before = diffusion_service.get_memory_usage()
        
        emit_progress_update(task_id, 'processing', 'Generating transformed image...', 40)
        
        # Generate the transformed image
        result_image = diffusion_service.generate_image(
            image=image,
            prompt=prompt,
            model_name=model_name,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            seed=seed
        )
        
        if result_image is None:
            raise RuntimeError("Image generation failed")
        
        emit_progress_update(task_id, 'processing', 'Saving result...', 80)
        
        # Generate result filename
        result_filename = f"result_{uuid.uuid4()}.jpg"
        
        # Upload result image
        result_url = storage_service.upload_image(result_image, result_filename, 'results')
        
        # Calculate processing metrics
        processing_time = (datetime.utcnow() - transformation.started_at).total_seconds()
        memory_after = diffusion_service.get_memory_usage()
        gpu_memory_used = memory_after.get('gpu_allocated', 0) - memory_before.get('gpu_allocated', 0)
        
        # Update transformation record
        transformation.status = 'completed'
        transformation.completed_at = datetime.utcnow()
        transformation.result_filename = result_filename
        transformation.result_url = result_url
        transformation.result_size = len(result_image.tobytes()) if result_image else 0
        transformation.processing_time = processing_time
        transformation.gpu_memory_used = gpu_memory_used
        
        # Update user statistics
        user = User.query.get(user_id)
        if user:
            user.total_transformations += 1
        
        db.session.commit()
        
        emit_progress_update(task_id, 'completed', 'Transformation completed successfully!', 100)
        
        logger.info("Image transformation completed", 
                   task_id=task_id, 
                   processing_time=processing_time,
                   model_name=model_name)
        
        return {
            'status': 'completed',
            'result_url': result_url,
            'processing_time': processing_time,
            'transformation_id': str(transformation.id)
        }
        
    except Exception as e:
        logger.error("Image transformation failed", 
                    task_id=task_id, 
                    error=str(e),
                    model_name=model_name)
        
        # Update transformation status to failed
        try:
            transformation = Transformation.query.filter_by(task_id=task_id).first()
            if transformation:
                transformation.status = 'failed'
                transformation.completed_at = datetime.utcnow()
                transformation.error_message = str(e)
                
                if transformation.started_at:
                    transformation.processing_time = (
                        datetime.utcnow() - transformation.started_at
                    ).total_seconds()
                
                db.session.commit()
        except Exception as db_error:
            logger.error("Failed to update transformation status", 
                        task_id=task_id, 
                        error=str(db_error))
        
        emit_progress_update(task_id, 'failed', f'Transformation failed: {str(e)}', 0)
        
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        # Clean up GPU memory
        try:
            diffusion_service.get_memory_usage()  # This will trigger cleanup if needed
        except:
            pass

def emit_progress_update(task_id: str, status: str, message: str, progress: int):
    """Emit progress update via WebSocket"""
    try:
        from app import socketio
        
        socketio.emit('transformation_progress', {
            'task_id': task_id,
            'status': status,
            'message': message,
            'progress': progress,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'task_{task_id}')
        
    except Exception as e:
        logger.warning("Failed to emit progress update", 
                      task_id=task_id, 
                      error=str(e))

# Create Celery task from the function
try:
    from app import celery
    process_image_task = celery.task(process_image_task)
except ImportError:
    # During initial setup, celery might not be available
    pass
