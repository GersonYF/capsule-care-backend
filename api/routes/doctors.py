from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.extensions import db
from api.models import Doctor, UserDoctor

doctors_bp = Blueprint('doctors', __name__, url_prefix='/api/doctors')

# Doctor CRUD
@doctors_bp.route('', methods=['GET'])
@jwt_required()
def get_doctors():
    """Get all doctors"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Doctor.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Doctor.first_name.ilike(f'%{search}%'),
                Doctor.last_name.ilike(f'%{search}%'),
                Doctor.specialty.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'doctors': [doc.to_dict() for doc in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@doctors_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_doctor(id):
    """Get a specific doctor"""
    doctor = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict()), 200

@doctors_bp.route('', methods=['POST'])
@jwt_required()
def create_doctor():
    """Create a new doctor"""
    data = request.get_json()
    
    if not data.get('first_name') or not data.get('last_name'):
        return jsonify({'error': 'First name and last name are required'}), 400
    
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        specialty=data.get('specialty'),
        license_number=data.get('license_number'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        notes=data.get('notes')
    )
    
    db.session.add(doctor)
    db.session.commit()
    
    return jsonify({
        'message': 'Doctor created successfully',
        'doctor': doctor.to_dict()
    }), 201

@doctors_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_doctor(id):
    """Update a doctor"""
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()
    
    if 'first_name' in data:
        doctor.first_name = data['first_name']
    if 'last_name' in data:
        doctor.last_name = data['last_name']
    if 'specialty' in data:
        doctor.specialty = data['specialty']
    if 'license_number' in data:
        doctor.license_number = data['license_number']
    if 'phone' in data:
        doctor.phone = data['phone']
    if 'email' in data:
        doctor.email = data['email']
    if 'address' in data:
        doctor.address = data['address']
    if 'notes' in data:
        doctor.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Doctor updated successfully',
        'doctor': doctor.to_dict()
    }), 200

@doctors_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(id):
    """Soft delete a doctor"""
    doctor = Doctor.query.get_or_404(id)
    doctor.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Doctor deleted successfully'}), 200

# User Doctors (Relationships)
@doctors_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_doctors():
    """Get current user's doctors"""
    current_user_id = int(get_jwt_identity())
    
    user_doctors = UserDoctor.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for ud in user_doctors:
        user_doc_dict = ud.to_dict()
        if ud.doctor:
            user_doc_dict['doctor'] = ud.doctor.to_dict()
        result.append(user_doc_dict)
    
    return jsonify({'doctors': result}), 200

@doctors_bp.route('/user/<int:id>', methods=['GET'])
@jwt_required()
def get_user_doctor(id):
    """Get a specific user doctor relationship"""
    current_user_id = int(get_jwt_identity())
    user_doc = UserDoctor.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    result = user_doc.to_dict()
    if user_doc.doctor:
        result['doctor'] = user_doc.doctor.to_dict()
    
    return jsonify(result), 200

@doctors_bp.route('/user', methods=['POST'])
@jwt_required()
def create_user_doctor():
    """Add a doctor to current user"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('doctor_id'):
        return jsonify({'error': 'doctor_id is required'}), 400
    
    user_doc = UserDoctor(
        user_id=current_user_id,
        doctor_id=data['doctor_id'],
        relationship_type=data.get('relationship_type'),
        is_primary=data.get('is_primary', False),
        relationship_start_date=data.get('relationship_start_date'),
        relationship_end_date=data.get('relationship_end_date'),
        notes=data.get('notes')
    )
    
    db.session.add(user_doc)
    db.session.commit()
    
    return jsonify({
        'message': 'Doctor added to user successfully',
        'user_doctor': user_doc.to_dict()
    }), 201

@doctors_bp.route('/user/<int:id>', methods=['PUT'])
@jwt_required()
def update_user_doctor(id):
    """Update a user doctor relationship"""
    current_user_id = int(get_jwt_identity())
    user_doc = UserDoctor.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'relationship_type' in data:
        user_doc.relationship_type = data['relationship_type']
    if 'is_primary' in data:
        user_doc.is_primary = data['is_primary']
    if 'relationship_start_date' in data:
        user_doc.relationship_start_date = data['relationship_start_date']
    if 'relationship_end_date' in data:
        user_doc.relationship_end_date = data['relationship_end_date']
    if 'notes' in data:
        user_doc.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User doctor relationship updated successfully',
        'user_doctor': user_doc.to_dict()
    }), 200

@doctors_bp.route('/user/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user_doctor(id):
    """Delete a user doctor relationship"""
    current_user_id = int(get_jwt_identity())
    user_doc = UserDoctor.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(user_doc)
    db.session.commit()
    
    return jsonify({'message': 'Doctor removed from user successfully'}), 200
