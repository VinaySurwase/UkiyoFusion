from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import structlog

from models import db, User, GalleryItem, Transformation

logger = structlog.get_logger()
gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('', methods=['GET'])
@jwt_required()
def get_user_gallery():
    """Get user's gallery items"""
    try:
        current_user_id = get_jwt_identity()
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 12, type=int), 50)
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        
        # Build query
        query = GalleryItem.query.filter_by(user_id=current_user_id)
        
        # Filter by tags if provided
        if tags:
            for tag in tags:
                if tag.strip():
                    query = query.filter(GalleryItem.tags.contains(tag.strip()))
        
        # Order by creation date (newest first)
        query = query.order_by(GalleryItem.created_at.desc())
        
        # Paginate
        gallery_items = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'gallery_items': [item.to_dict() for item in gallery_items.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': gallery_items.total,
                'pages': gallery_items.pages,
                'has_next': gallery_items.has_next,
                'has_prev': gallery_items.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error("Get gallery error", error=str(e))
        return jsonify({'error': 'Failed to get gallery items'}), 500

@gallery_bp.route('', methods=['POST'])
@jwt_required()
def create_gallery_item():
    """Create new gallery item from transformation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('transformation_id') or not data.get('title'):
            return jsonify({'error': 'transformation_id and title are required'}), 400
        
        # Check if transformation exists and belongs to user
        transformation = Transformation.query.filter_by(
            id=data['transformation_id'],
            user_id=current_user_id
        ).first()
        
        if not transformation:
            return jsonify({'error': 'Transformation not found'}), 404
        
        if transformation.status != 'completed':
            return jsonify({'error': 'Transformation must be completed'}), 400
        
        # Check if gallery item already exists for this transformation
        existing_item = GalleryItem.query.filter_by(
            transformation_id=transformation.id,
            user_id=current_user_id
        ).first()
        
        if existing_item:
            return jsonify({'error': 'Gallery item already exists for this transformation'}), 409
        
        # Create gallery item
        gallery_item = GalleryItem(
            user_id=current_user_id,
            transformation_id=transformation.id,
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            tags=','.join([tag.strip() for tag in data.get('tags', []) if tag.strip()]),
            is_public=data.get('is_public', False)
        )
        
        # Generate share token if public
        if gallery_item.is_public:
            gallery_item.generate_share_token()
        
        db.session.add(gallery_item)
        db.session.commit()
        
        logger.info("Gallery item created", 
                   gallery_item_id=str(gallery_item.id), 
                   user_id=current_user_id)
        
        return jsonify({
            'message': 'Gallery item created successfully',
            'gallery_item': gallery_item.to_dict()
        }), 201
        
    except Exception as e:
        logger.error("Create gallery item error", error=str(e))
        db.session.rollback()
        return jsonify({'error': 'Failed to create gallery item'}), 500

@gallery_bp.route('/<gallery_item_id>', methods=['GET'])
def get_gallery_item(gallery_item_id):
    """Get specific gallery item (public or owned by user)"""
    try:
        gallery_item = GalleryItem.query.get(gallery_item_id)
        
        if not gallery_item:
            return jsonify({'error': 'Gallery item not found'}), 404
        
        # Check access permissions
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        current_user_id = None
        
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except:
            pass
        
        # Allow access if item is public or user owns it
        if not gallery_item.is_public and gallery_item.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Increment view count (only for public items or different users)
        if gallery_item.is_public and gallery_item.user_id != current_user_id:
            gallery_item.view_count += 1
            db.session.commit()
        
        return jsonify({
            'gallery_item': gallery_item.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Get gallery item error", error=str(e), gallery_item_id=gallery_item_id)
        return jsonify({'error': 'Failed to get gallery item'}), 500

@gallery_bp.route('/<gallery_item_id>', methods=['PUT'])
@jwt_required()
def update_gallery_item(gallery_item_id):
    """Update gallery item"""
    try:
        current_user_id = get_jwt_identity()
        
        gallery_item = GalleryItem.query.filter_by(
            id=gallery_item_id,
            user_id=current_user_id
        ).first()
        
        if not gallery_item:
            return jsonify({'error': 'Gallery item not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            gallery_item.title = data['title'].strip()
        
        if 'description' in data:
            gallery_item.description = data['description'].strip()
        
        if 'tags' in data:
            gallery_item.tags = ','.join([tag.strip() for tag in data['tags'] if tag.strip()])
        
        if 'is_public' in data:
            gallery_item.is_public = data['is_public']
            
            # Generate or remove share token based on public status
            if gallery_item.is_public and not gallery_item.share_token:
                gallery_item.generate_share_token()
            elif not gallery_item.is_public:
                gallery_item.share_token = None
        
        gallery_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info("Gallery item updated", 
                   gallery_item_id=gallery_item_id, 
                   user_id=current_user_id)
        
        return jsonify({
            'message': 'Gallery item updated successfully',
            'gallery_item': gallery_item.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Update gallery item error", error=str(e), gallery_item_id=gallery_item_id)
        db.session.rollback()
        return jsonify({'error': 'Failed to update gallery item'}), 500

@gallery_bp.route('/<gallery_item_id>', methods=['DELETE'])
@jwt_required()
def delete_gallery_item(gallery_item_id):
    """Delete gallery item"""
    try:
        current_user_id = get_jwt_identity()
        
        gallery_item = GalleryItem.query.filter_by(
            id=gallery_item_id,
            user_id=current_user_id
        ).first()
        
        if not gallery_item:
            return jsonify({'error': 'Gallery item not found'}), 404
        
        db.session.delete(gallery_item)
        db.session.commit()
        
        logger.info("Gallery item deleted", 
                   gallery_item_id=gallery_item_id, 
                   user_id=current_user_id)
        
        return jsonify({'message': 'Gallery item deleted successfully'}), 200
        
    except Exception as e:
        logger.error("Delete gallery item error", error=str(e), gallery_item_id=gallery_item_id)
        db.session.rollback()
        return jsonify({'error': 'Failed to delete gallery item'}), 500

@gallery_bp.route('/public', methods=['GET'])
def get_public_gallery():
    """Get public gallery items"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 12, type=int), 50)
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        
        # Build query for public items
        query = GalleryItem.query.filter_by(is_public=True)
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        # Filter by tags if provided
        if tags:
            for tag in tags:
                if tag.strip():
                    query = query.filter(GalleryItem.tags.contains(tag.strip()))
        
        # Order by view count for featured, creation date otherwise
        if featured_only:
            query = query.order_by(GalleryItem.view_count.desc(), GalleryItem.created_at.desc())
        else:
            query = query.order_by(GalleryItem.created_at.desc())
        
        # Paginate
        gallery_items = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'gallery_items': [item.to_dict() for item in gallery_items.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': gallery_items.total,
                'pages': gallery_items.pages,
                'has_next': gallery_items.has_next,
                'has_prev': gallery_items.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error("Get public gallery error", error=str(e))
        return jsonify({'error': 'Failed to get public gallery items'}), 500

@gallery_bp.route('/share/<share_token>', methods=['GET'])
def get_shared_gallery_item(share_token):
    """Get gallery item by share token"""
    try:
        gallery_item = GalleryItem.query.filter_by(
            share_token=share_token,
            is_public=True
        ).first()
        
        if not gallery_item:
            return jsonify({'error': 'Shared item not found'}), 404
        
        # Increment view count
        gallery_item.view_count += 1
        db.session.commit()
        
        return jsonify({
            'gallery_item': gallery_item.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Get shared gallery item error", error=str(e), share_token=share_token)
        return jsonify({'error': 'Failed to get shared item'}), 500
