from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Notification, MedicationIntake
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get current user's notifications"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if unread_only:
        query = query.filter(Notification.read_at.is_(None))
    
    pagination = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [n.to_dict() for n in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@notifications_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_notification(id):
    """Get a specific notification"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    return jsonify(notification.to_dict()), 200

@notifications_bp.route('/<int:id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(id):
    """Mark a notification as read"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    notification.read_at = datetime.utcnow()
    notification.status = 'read'
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200

@notifications_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read"""
    current_user_id = get_jwt_identity()
    
    Notification.query.filter_by(
        user_id=current_user_id
    ).filter(Notification.read_at.is_(None)).update({
        'read_at': datetime.utcnow(),
        'status': 'read'
    })
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200

@notifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_notification(id):
    """Delete a notification"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted successfully'}), 200

# Medication Intake Tracking
@notifications_bp.route('/intake', methods=['GET'])
@jwt_required()
def get_intakes():
    """Get medication intake history"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get user's medication intakes through user_medications
    from models import UserMedication
    user_med_ids = [um.id for um in UserMedication.query.filter_by(user_id=current_user_id).all()]
    
    pagination = MedicationIntake.query.filter(
        MedicationIntake.user_medication_id.in_(user_med_ids)
    ).order_by(MedicationIntake.status_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'intakes': [i.to_dict() for i in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@notifications_bp.route('/intake', methods=['POST'])
@jwt_required()
def create_intake():
    """Log a medication intake"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('user_medication_id'):
        return jsonify({'error': 'user_medication_id is required'}), 400
    
    # Verify user owns the medication
    from models import UserMedication
    user_med = UserMedication.query.get_or_404(data['user_medication_id'])
    if user_med.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    intake = MedicationIntake(
        user_medication_id=data['user_medication_id'],
        reminder_log_id=data.get('reminder_log_id'),
        status_at=data.get('status_at', datetime.utcnow()),
        dosage_taken=data.get('dosage_taken'),
        status=data.get('status', 'taken'),
        notes=data.get('notes'),
        side_effects_reported=data.get('side_effects_reported')
    )
    
    db.session.add(intake)
    db.session.commit()
    
    return jsonify({
        'message': 'Medication intake logged successfully',
        'intake': intake.to_dict()
    }), 201

@notifications_bp.route('/intake/<int:id>', methods=['PUT'])
@jwt_required()
def update_intake(id):
    """Update a medication intake log"""
    current_user_id = get_jwt_identity()
    
    intake = MedicationIntake.query.get_or_404(id)
    
    # Verify user owns this intake
    from models import UserMedication
    user_med = UserMedication.query.get_or_404(intake.user_medication_id)
    if user_med.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'status_at' in data:
        intake.status_at = data['status_at']
    if 'dosage_taken' in data:
        intake.dosage_taken = data['dosage_taken']
    if 'status' in data:
        intake.status = data['status']
    if 'notes' in data:
        intake.notes = data['notes']
    if 'side_effects_reported' in data:
        intake.side_effects_reported = data['side_effects_reported']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Intake log updated successfully',
        'intake': intake.to_dict()
    }), 200
