from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.extensions import db
from api.models import MediaFile

media_bp = Blueprint('media', __name__, url_prefix='/api/media')

@media_bp.route('', methods=['GET'])
@jwt_required()
def get_media_files():
    """Get current user's media files"""
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    
    query = MediaFile.query.filter_by(user_id=current_user_id)
    
    if entity_type:
        query = query.filter_by(related_entity_type=entity_type)
    
    if entity_id:
        query = query.filter_by(related_entity_id=entity_id)
    
    pagination = query.order_by(MediaFile.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'media_files': [mf.to_dict() for mf in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@media_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_media_file(id):
    """Get a specific media file"""
    current_user_id = int(get_jwt_identity())
    
    media_file = MediaFile.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    return jsonify(media_file.to_dict()), 200

@media_bp.route('', methods=['POST'])
@jwt_required()
def create_media_file():
    """Create a new media file record"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('file_path'):
        return jsonify({'error': 'file_path is required'}), 400
    
    media_file = MediaFile(
        user_id=current_user_id,
        related_entity_id=data.get('related_entity_id'),
        related_entity_type=data.get('related_entity_type'),
        original_name=data.get('original_name'),
        file_path=data['file_path'],
        file_type=data.get('file_type'),
        mime_type=data.get('mime_type'),
        file_size=data.get('file_size'),
        file_metadata=data.get('file_metadata'),
        description=data.get('description')
    )
    
    db.session.add(media_file)
    db.session.commit()
    
    return jsonify({
        'message': 'Media file created successfully',
        'media_file': media_file.to_dict()
    }), 201

@media_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_media_file(id):
    """Update a media file record"""
    current_user_id = int(get_jwt_identity())
    
    media_file = MediaFile.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'description' in data:
        media_file.description = data['description']
    if 'file_metadata' in data:
        media_file.file_metadata = data['file_metadata']
    if 'is_processed' in data:
        media_file.is_processed = data['is_processed']
    if 'ai_analysis_result' in data:
        media_file.ai_analysis_result = data['ai_analysis_result']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Media file updated successfully',
        'media_file': media_file.to_dict()
    }), 200

@media_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_media_file(id):
    """Delete a media file record"""
    current_user_id = int(get_jwt_identity())
    
    media_file = MediaFile.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(media_file)
    db.session.commit()
    
    return jsonify({'message': 'Media file deleted successfully'}), 200
