from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import structlog

from models import db, User, Transformation
from services.diffusion_service import DiffusionService
from services.storage_service import StorageService
from utils.validators import allowed_file, validate_image
from tasks.image_processing import process_image_task

logger = structlog.get_logger()
transform_bp = Blueprint('transform', __name__)

# Initialize services
diffusion_service = DiffusionService()
storage_service = StorageService()

@transform_bp.route('/models', methods=['GET'])
@jwt_required()
def get_available_models():
    """Get list of available diffusion models"""
    try:
        models = diffusion_service.get_available_models()
        return jsonify({'models': models}), 200
    
    except Exception as e:
        logger.error("Error getting models", error=str(e))
        return jsonify({'error': 'Failed to get available models'}), 500

@transform_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_and_transform():
    """Upload image and start transformation process"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Supported: JPG, PNG, WebP'}), 400
        
        # Validate image content
        try:
            is_valid, error_msg = validate_image(file)
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        except Exception as e:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Get transformation parameters
        model_name = request.form.get('model_name', current_app.config['DEFAULT_MODEL'])
        prompt = request.form.get('prompt', '')
        negative_prompt = request.form.get('negative_prompt', '')
        strength = float(request.form.get('strength', 0.8))
        guidance_scale = float(request.form.get('guidance_scale', 7.5))
        num_inference_steps = int(request.form.get('num_inference_steps', 20))
        seed = request.form.get('seed')
        
        # Validate parameters
        if strength < 0.1 or strength > 1.0:
            return jsonify({'error': 'Strength must be between 0.1 and 1.0'}), 400
        
        if guidance_scale < 1.0 or guidance_scale > 20.0:
            return jsonify({'error': 'Guidance scale must be between 1.0 and 20.0'}), 400
        
        if num_inference_steps < 10 or num_inference_steps > 100:
            return jsonify({'error': 'Number of inference steps must be between 10 and 100'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Upload original image
        original_url = storage_service.upload_file(file, unique_filename)
        
        # Create transformation record
        task_id = str(uuid.uuid4())
        transformation = Transformation(
            user_id=current_user_id,
            task_id=task_id,
            original_filename=filename,
            original_url=original_url,
            original_size=len(file.read()),
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            seed=int(seed) if seed else None,
            status='pending'
        )
        
        db.session.add(transformation)
        db.session.commit()
        
        # Start background processing
        file.seek(0)  # Reset file pointer
        process_image_task.delay(
            task_id=task_id,
            user_id=current_user_id,
            image_data=file.read(),
            filename=unique_filename,
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            seed=int(seed) if seed else None
        )
        
        logger.info("Transformation started", task_id=task_id, user_id=current_user_id)
        
        return jsonify({
            'message': 'Transformation started',
            'task_id': task_id,
            'transformation': transformation.to_dict()
        }), 202
        
    except Exception as e:
        logger.error("Upload and transform error", error=str(e))
        db.session.rollback()
        return jsonify({'error': 'Failed to start transformation'}), 500

@transform_bp.route('/status/<task_id>', methods=['GET'])
@jwt_required()
def get_transform_status(task_id):
    """Get transformation status"""
    try:
        current_user_id = get_jwt_identity()
        
        transformation = Transformation.query.filter_by(
            task_id=task_id,
            user_id=current_user_id
        ).first()
        
        if not transformation:
            return jsonify({'error': 'Transformation not found'}), 404
        
        return jsonify({
            'transformation': transformation.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Get status error", error=str(e), task_id=task_id)
        return jsonify({'error': 'Failed to get transformation status'}), 500

@transform_bp.route('/result/<task_id>', methods=['GET'])
@jwt_required()
def get_transform_result(task_id):
    """Get transformation result"""
    try:
        current_user_id = get_jwt_identity()
        
        transformation = Transformation.query.filter_by(
            task_id=task_id,
            user_id=current_user_id
        ).first()
        
        if not transformation:
            return jsonify({'error': 'Transformation not found'}), 404
        
        if transformation.status != 'completed':
            return jsonify({
                'error': 'Transformation not completed',
                'status': transformation.status
            }), 400
        
        return jsonify({
            'transformation': transformation.to_dict(),
            'download_url': transformation.result_url
        }), 200
        
    except Exception as e:
        logger.error("Get result error", error=str(e), task_id=task_id)
        return jsonify({'error': 'Failed to get transformation result'}), 500

@transform_bp.route('/history', methods=['GET'])
@jwt_required()
def get_transform_history():
    """Get user's transformation history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        status = request.args.get('status')
        
        # Build query
        query = Transformation.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by creation date (newest first)
        query = query.order_by(Transformation.created_at.desc())
        
        # Paginate
        transformations = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'transformations': [t.to_dict() for t in transformations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transformations.total,
                'pages': transformations.pages,
                'has_next': transformations.has_next,
                'has_prev': transformations.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error("Get history error", error=str(e))
        return jsonify({'error': 'Failed to get transformation history'}), 500

@transform_bp.route('/cancel/<task_id>', methods=['POST'])
@jwt_required()
def cancel_transformation(task_id):
    """Cancel pending transformation"""
    try:
        current_user_id = get_jwt_identity()
        
        transformation = Transformation.query.filter_by(
            task_id=task_id,
            user_id=current_user_id
        ).first()
        
        if not transformation:
            return jsonify({'error': 'Transformation not found'}), 404
        
        if transformation.status not in ['pending', 'processing']:
            return jsonify({
                'error': 'Cannot cancel transformation',
                'status': transformation.status
            }), 400
        
        # Cancel Celery task
        from app import celery
        celery.control.revoke(task_id, terminate=True)
        
        # Update status
        transformation.status = 'failed'
        transformation.error_message = 'Cancelled by user'
        db.session.commit()
        
        logger.info("Transformation cancelled", task_id=task_id, user_id=current_user_id)
        
        return jsonify({
            'message': 'Transformation cancelled',
            'transformation': transformation.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Cancel transformation error", error=str(e), task_id=task_id)
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel transformation'}), 500

@transform_bp.route('/delete/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_transformation(task_id):
    """Delete transformation and associated files"""
    try:
        current_user_id = get_jwt_identity()
        
        transformation = Transformation.query.filter_by(
            task_id=task_id,
            user_id=current_user_id
        ).first()
        
        if not transformation:
            return jsonify({'error': 'Transformation not found'}), 404
        
        # Delete files from storage
        try:
            if transformation.original_url:
                storage_service.delete_file(transformation.original_url)
            if transformation.result_url:
                storage_service.delete_file(transformation.result_url)
        except Exception as e:
            logger.warning("Failed to delete files from storage", error=str(e))
        
        # Delete from database
        db.session.delete(transformation)
        db.session.commit()
        
        logger.info("Transformation deleted", task_id=task_id, user_id=current_user_id)
        
        return jsonify({'message': 'Transformation deleted'}), 200
        
    except Exception as e:
        logger.error("Delete transformation error", error=str(e), task_id=task_id)
        db.session.rollback()
        return jsonify({'error': 'Failed to delete transformation'}), 500
