from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Medication, UserMedication

medications_bp = Blueprint('medications', __name__, url_prefix='/api/medications')

# Medication CRUD
@medications_bp.route('', methods=['GET'])
@jwt_required()
def get_medications():
    """Get all medications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Medication.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Medication.name.ilike(f'%{search}%'),
                Medication.generic_name.ilike(f'%{search}%'),
                Medication.brand_name.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'medications': [med.to_dict() for med in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@medications_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_medication(id):
    """Get a specific medication"""
    medication = Medication.query.get_or_404(id)
    return jsonify(medication.to_dict()), 200

@medications_bp.route('', methods=['POST'])
@jwt_required()
def create_medication():
    """Create a new medication"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Medication name is required'}), 400
    
    medication = Medication(
        name=data['name'],
        generic_name=data.get('generic_name'),
        brand_name=data.get('brand_name'),
        description=data.get('description'),
        manufacturer=data.get('manufacturer'),
        dosage_form=data.get('dosage_form'),
        strength=data.get('strength'),
        route_of_administration=data.get('route_of_administration'),
        uses=data.get('uses'),
        contraindications=data.get('contraindications'),
        storage_instructions=data.get('storage_instructions'),
        barcode=data.get('barcode'),
        image_url=data.get('image_url'),
        requires_prescription=data.get('requires_prescription', True)
    )
    
    db.session.add(medication)
    db.session.commit()
    
    return jsonify({
        'message': 'Medication created successfully',
        'medication': medication.to_dict()
    }), 201

@medications_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_medication(id):
    """Update a medication"""
    medication = Medication.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        medication.name = data['name']
    if 'generic_name' in data:
        medication.generic_name = data['generic_name']
    if 'brand_name' in data:
        medication.brand_name = data['brand_name']
    if 'description' in data:
        medication.description = data['description']
    if 'manufacturer' in data:
        medication.manufacturer = data['manufacturer']
    if 'dosage_form' in data:
        medication.dosage_form = data['dosage_form']
    if 'strength' in data:
        medication.strength = data['strength']
    if 'route_of_administration' in data:
        medication.route_of_administration = data['route_of_administration']
    if 'uses' in data:
        medication.uses = data['uses']
    if 'contraindications' in data:
        medication.contraindications = data['contraindications']
    if 'storage_instructions' in data:
        medication.storage_instructions = data['storage_instructions']
    if 'barcode' in data:
        medication.barcode = data['barcode']
    if 'image_url' in data:
        medication.image_url = data['image_url']
    if 'requires_prescription' in data:
        medication.requires_prescription = data['requires_prescription']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Medication updated successfully',
        'medication': medication.to_dict()
    }), 200

@medications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_medication(id):
    """Soft delete a medication"""
    medication = Medication.query.get_or_404(id)
    medication.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Medication deleted successfully'}), 200

# User Medications CRUD
@medications_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_medications():
    """Get current user's medications"""
    current_user_id = get_jwt_identity()
    
    medications = UserMedication.query.filter_by(
        user_id=current_user_id,
        is_active=True
    ).all()
    
    result = []
    for um in medications:
        user_med_dict = um.to_dict()
        if um.medication:
            user_med_dict['medication'] = um.medication.to_dict()
        result.append(user_med_dict)
    
    return jsonify({'medications': result}), 200

@medications_bp.route('/user/<int:id>', methods=['GET'])
@jwt_required()
def get_user_medication(id):
    """Get a specific user medication"""
    current_user_id = get_jwt_identity()
    user_med = UserMedication.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    result = user_med.to_dict()
    if user_med.medication:
        result['medication'] = user_med.medication.to_dict()
    
    return jsonify(result), 200

@medications_bp.route('/user', methods=['POST'])
@jwt_required()
def create_user_medication():
    """Add a medication to current user"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('medication_id'):
        return jsonify({'error': 'medication_id is required'}), 400
    
    user_med = UserMedication(
        user_id=current_user_id,
        medication_id=data['medication_id'],
        custom_name=data.get('custom_name'),
        prescribed_dosage=data.get('prescribed_dosage'),
        prescribed_frequency=data.get('prescribed_frequency'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        doctor_instructions=data.get('doctor_instructions'),
        notes=data.get('notes')
    )
    
    db.session.add(user_med)
    db.session.commit()
    
    return jsonify({
        'message': 'Medication added to user successfully',
        'user_medication': user_med.to_dict()
    }), 201

@medications_bp.route('/user/<int:id>', methods=['PUT'])
@jwt_required()
def update_user_medication(id):
    """Update a user medication"""
    current_user_id = get_jwt_identity()
    user_med = UserMedication.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'custom_name' in data:
        user_med.custom_name = data['custom_name']
    if 'prescribed_dosage' in data:
        user_med.prescribed_dosage = data['prescribed_dosage']
    if 'prescribed_frequency' in data:
        user_med.prescribed_frequency = data['prescribed_frequency']
    if 'start_date' in data:
        user_med.start_date = data['start_date']
    if 'end_date' in data:
        user_med.end_date = data['end_date']
    if 'doctor_instructions' in data:
        user_med.doctor_instructions = data['doctor_instructions']
    if 'notes' in data:
        user_med.notes = data['notes']
    if 'is_active' in data:
        user_med.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User medication updated successfully',
        'user_medication': user_med.to_dict()
    }), 200

@medications_bp.route('/user/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user_medication(id):
    """Soft delete a user medication"""
    current_user_id = get_jwt_identity()
    user_med = UserMedication.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    user_med.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User medication deleted successfully'}), 200
