from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, UserSetting, EmergencyContact, ActivityLog
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict()), 200

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'date_of_birth' in data:
        user.date_of_birth = data['date_of_birth']
    if 'gender' in data:
        user.gender = data['gender']
    if 'language' in data:
        user.language = data['language']
    if 'profile_image_url' in data:
        user.profile_image_url = data['profile_image_url']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

# User Settings
@users_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get current user's settings"""
    current_user_id = int(get_jwt_identity())
    settings = UserSetting.query.filter_by(user_id=current_user_id).all()
    return jsonify({'settings': [s.to_dict() for s in settings]}), 200

@users_bp.route('/settings', methods=['POST'])
@jwt_required()
def create_setting():
    """Create a new user setting"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('setting_key'):
        return jsonify({'error': 'setting_key is required'}), 400
    
    # Check if setting already exists
    existing = UserSetting.query.filter_by(
        user_id=current_user_id,
        setting_key=data['setting_key']
    ).first()
    
    if existing:
        existing.setting_value = data.get('setting_value')
        existing.data_type = data.get('data_type')
        existing.description = data.get('description')
        db.session.commit()
        return jsonify({
            'message': 'Setting updated successfully',
            'setting': existing.to_dict()
        }), 200
    
    setting = UserSetting(
        user_id=current_user_id,
        setting_key=data['setting_key'],
        setting_value=data.get('setting_value'),
        data_type=data.get('data_type'),
        description=data.get('description')
    )
    
    db.session.add(setting)
    db.session.commit()
    
    return jsonify({
        'message': 'Setting created successfully',
        'setting': setting.to_dict()
    }), 201

@users_bp.route('/settings/<int:id>', methods=['PUT'])
@jwt_required()
def update_setting(id):
    """Update a user setting"""
    current_user_id = int(get_jwt_identity())
    
    setting = UserSetting.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'setting_value' in data:
        setting.setting_value = data['setting_value']
    if 'data_type' in data:
        setting.data_type = data['data_type']
    if 'description' in data:
        setting.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Setting updated successfully',
        'setting': setting.to_dict()
    }), 200

@users_bp.route('/settings/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_setting(id):
    """Delete a user setting"""
    current_user_id = int(get_jwt_identity())
    
    setting = UserSetting.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(setting)
    db.session.commit()
    
    return jsonify({'message': 'Setting deleted successfully'}), 200

# Emergency Contacts
@users_bp.route('/emergency-contacts', methods=['GET'])
@jwt_required()
def get_emergency_contacts():
    """Get current user's emergency contacts"""
    current_user_id = int(get_jwt_identity())
    contacts = EmergencyContact.query.filter_by(user_id=current_user_id).all()
    return jsonify({'contacts': [c.to_dict() for c in contacts]}), 200

@users_bp.route('/emergency-contacts/<int:id>', methods=['GET'])
@jwt_required()
def get_emergency_contact(id):
    """Get a specific emergency contact"""
    current_user_id = int(get_jwt_identity())
    
    contact = EmergencyContact.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    return jsonify(contact.to_dict()), 200

@users_bp.route('/emergency-contacts', methods=['POST'])
@jwt_required()
def create_emergency_contact():
    """Create a new emergency contact"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    contact = EmergencyContact(
        user_id=current_user_id,
        name=data['name'],
        relationship=data.get('relationship'),
        phone=data.get('phone'),
        email=data.get('email'),
        is_primary=data.get('is_primary', False),
        notify_missed_doses=data.get('notify_missed_doses', False)
    )
    
    db.session.add(contact)
    db.session.commit()
    
    return jsonify({
        'message': 'Emergency contact created successfully',
        'contact': contact.to_dict()
    }), 201

@users_bp.route('/emergency-contacts/<int:id>', methods=['PUT'])
@jwt_required()
def update_emergency_contact(id):
    """Update an emergency contact"""
    current_user_id = int(get_jwt_identity())
    
    contact = EmergencyContact.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'name' in data:
        contact.name = data['name']
    if 'relationship' in data:
        contact.relationship = data['relationship']
    if 'phone' in data:
        contact.phone = data['phone']
    if 'email' in data:
        contact.email = data['email']
    if 'is_primary' in data:
        contact.is_primary = data['is_primary']
    if 'notify_missed_doses' in data:
        contact.notify_missed_doses = data['notify_missed_doses']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Emergency contact updated successfully',
        'contact': contact.to_dict()
    }), 200

@users_bp.route('/emergency-contacts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_emergency_contact(id):
    """Delete an emergency contact"""
    current_user_id = int(get_jwt_identity())
    
    contact = EmergencyContact.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({'message': 'Emergency contact deleted successfully'}), 200

# Activity Logs
@users_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
def get_activity_logs():
    """Get current user's activity logs"""
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = ActivityLog.query.filter_by(
        user_id=current_user_id
    ).order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200
