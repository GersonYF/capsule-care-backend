from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'message': 'Capsule Care API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': {
                'POST /api/auth/register': 'Register a new user',
                'POST /api/auth/login': 'Login and get JWT token',
                'GET /api/auth/profile': 'Get user profile (requires JWT)'
            },
            'users': {
                'GET /api/users/profile': 'Get user profile',
                'PUT /api/users/profile': 'Update user profile',
                'GET /api/users/settings': 'Get user settings',
                'POST /api/users/settings': 'Create/update setting',
                'GET /api/users/emergency-contacts': 'Get emergency contacts',
                'POST /api/users/emergency-contacts': 'Create emergency contact',
                'GET /api/users/activity-logs': 'Get activity logs'
            },
            'medications': {
                'GET /api/medications': 'Get all medications',
                'POST /api/medications': 'Create medication',
                'GET /api/medications/user': 'Get user medications',
                'POST /api/medications/user': 'Add medication to user'
            },
            'doctors': {
                'GET /api/doctors': 'Get all doctors',
                'POST /api/doctors': 'Create doctor',
                'GET /api/doctors/user': 'Get user doctors',
                'POST /api/doctors/user': 'Add doctor to user'
            },
            'reminders': {
                'GET /api/reminders': 'Get user reminders',
                'POST /api/reminders': 'Create reminder',
                'GET /api/reminders/:id/logs': 'Get reminder logs'
            },
            'prescriptions': {
                'GET /api/prescriptions': 'Get user prescriptions',
                'POST /api/prescriptions': 'Create prescription'
            },
            'notifications': {
                'GET /api/notifications': 'Get notifications',
                'PUT /api/notifications/:id/read': 'Mark as read',
                'GET /api/notifications/intake': 'Get medication intake logs',
                'POST /api/notifications/intake': 'Log medication intake'
            },
            'media': {
                'GET /api/media': 'Get media files',
                'POST /api/media': 'Upload media file'
            }
        }
    }), 200

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'medication-reminder-api'
    }), 200

@main_bp.route('/api/protected')
@jwt_required()
def protected():
    """Example protected route"""
    current_user_id = int(get_jwt_identity())
    return jsonify({
        'message': 'This is a protected route',
        'user_id': current_user_id
    }), 200
