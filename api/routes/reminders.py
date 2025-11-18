from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.extensions import db
from api.models import Reminder, ReminderLog, UserMedication
from tasks.notification_tasks import schedule_reminder
from datetime import datetime

reminders_bp = Blueprint('reminders', __name__, url_prefix='/api/reminders')

# Reminder CRUD
@reminders_bp.route('', methods=['GET'])
@jwt_required()
def get_reminders():
    """Get current user's reminders"""
    current_user_id = int(get_jwt_identity())
    
    # Get user's medications first
    user_med_ids = [um.id for um in UserMedication.query.filter_by(user_id=current_user_id).all()]
    
    reminders = Reminder.query.filter(
        Reminder.user_medication_id.in_(user_med_ids)
    ).all()
    
    result = []
    for reminder in reminders:
        reminder_dict = reminder.to_dict()
        if reminder.user_medication and reminder.user_medication.medication:
            reminder_dict['medication'] = reminder.user_medication.medication.to_dict()
        result.append(reminder_dict)
    
    return jsonify({'reminders': result}), 200

@reminders_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_reminder(id):
    """Get a specific reminder"""
    current_user_id = int(get_jwt_identity())
    
    reminder = Reminder.query.get_or_404(id)
    
    # Verify user owns this reminder
    if reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    result = reminder.to_dict()
    if reminder.user_medication and reminder.user_medication.medication:
        result['medication'] = reminder.user_medication.medication.to_dict()
    
    return jsonify(result), 200

@reminders_bp.route('', methods=['POST'])
@jwt_required()
def create_reminder():
    """Create a new reminder"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('user_medication_id'):
        return jsonify({'error': 'user_medication_id is required'}), 400
    
    # Verify user owns the medication
    user_med = UserMedication.query.get_or_404(data['user_medication_id'])
    if user_med.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    reminder = Reminder(
        user_medication_id=data['user_medication_id'],
        title=data.get('title'),
        description=data.get('description'),
        reminder_time=data.get('reminder_time'),
        time_of_week=data.get('time_of_week'),
        frequency_type=data.get('frequency_type', 'daily'),
        frequency_value=data.get('frequency_value', 1),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        event_enabled=data.get('event_enabled', True),
        calendar_reminder=data.get('calendar_reminder', False),
        push_notification=data.get('push_notification', True),
        email_notification=data.get('email_notification', False)
    )
    
    db.session.add(reminder)
    db.session.commit()
    
    # Programar el recordatorio en Celery si está habilitado
    if reminder.event_enabled and reminder.reminder_time and reminder.start_date:
        try:
            # Programar la primera notificación
            first_reminder_datetime = datetime.combine(
                reminder.start_date,
                reminder.reminder_time
            )
            if first_reminder_datetime > datetime.utcnow():
                schedule_reminder.delay(reminder.id, first_reminder_datetime)
        except Exception as e:
            print(f"Error scheduling reminder: {e}")
    
    return jsonify({
        'message': 'Reminder created successfully',
        'reminder': reminder.to_dict()
    }), 201

@reminders_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_reminder(id):
    """Update a reminder"""
    current_user_id = int(get_jwt_identity())
    reminder = Reminder.query.get_or_404(id)
    
    # Verify user owns this reminder
    if reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        reminder.title = data['title']
    if 'description' in data:
        reminder.description = data['description']
    if 'reminder_time' in data:
        reminder.reminder_time = data['reminder_time']
    if 'time_of_week' in data:
        reminder.time_of_week = data['time_of_week']
    if 'frequency_type' in data:
        reminder.frequency_type = data['frequency_type']
    if 'frequency_value' in data:
        reminder.frequency_value = data['frequency_value']
    if 'start_date' in data:
        reminder.start_date = data['start_date']
    if 'end_date' in data:
        reminder.end_date = data['end_date']
    if 'is_active' in data:
        reminder.is_active = data['is_active']
    if 'event_enabled' in data:
        reminder.event_enabled = data['event_enabled']
    if 'calendar_reminder' in data:
        reminder.calendar_reminder = data['calendar_reminder']
    if 'push_notification' in data:
        reminder.push_notification = data['push_notification']
    if 'email_notification' in data:
        reminder.email_notification = data['email_notification']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reminder updated successfully',
        'reminder': reminder.to_dict()
    }), 200

@reminders_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_reminder(id):
    """Delete a reminder"""
    current_user_id = int(get_jwt_identity())
    reminder = Reminder.query.get_or_404(id)
    
    # Verify user owns this reminder
    if reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    reminder.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Reminder deleted successfully'}), 200

# Reminder Logs
@reminders_bp.route('/<int:reminder_id>/logs', methods=['GET'])
@jwt_required()
def get_reminder_logs(reminder_id):
    """Get logs for a specific reminder"""
    current_user_id = int(get_jwt_identity())
    
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Verify user owns this reminder
    if reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = ReminderLog.query.filter_by(
        reminder_id=reminder_id
    ).order_by(ReminderLog.scheduled_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@reminders_bp.route('/logs/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_reminder_log(log_id):
    """Update a reminder log (mark as acknowledged, etc.)"""
    current_user_id = int(get_jwt_identity())
    
    log = ReminderLog.query.get_or_404(log_id)
    
    # Verify user owns this log
    if log.reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'status' in data:
        log.status = data['status']
    if 'actual_time' in data:
        log.actual_time = data['actual_time']
    if 'notes' in data:
        log.notes = data['notes']
    if 'log_metadata' in data:
        log.log_metadata = data['log_metadata']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reminder log updated successfully',
        'log': log.to_dict()
    }), 200

@reminders_bp.route('/test-notification/<int:id>', methods=['POST'])
@jwt_required()
def test_notification(id):
    """Enviar una notificación de prueba para un recordatorio"""
    current_user_id = int(get_jwt_identity())
    
    reminder = Reminder.query.get_or_404(id)
    
    # Verify user owns this reminder
    if reminder.user_medication.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from tasks.notification_tasks import send_reminder_notification
    
    # Enviar notificación inmediatamente
    result = send_reminder_notification.delay(reminder.id)
    
    return jsonify({
        'message': 'Test notification scheduled',
        'task_id': result.id
    }), 200
