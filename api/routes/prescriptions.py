from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Prescription

prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/api/prescriptions')

@prescriptions_bp.route('', methods=['GET'])
@jwt_required()
def get_prescriptions():
    """Get current user's prescriptions"""
    current_user_id = int(get_jwt_identity())
    
    status = request.args.get('status')
    
    query = Prescription.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    prescriptions = query.order_by(Prescription.prescribed_date.desc()).all()
    
    return jsonify({
        'prescriptions': [p.to_dict() for p in prescriptions]
    }), 200

@prescriptions_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_prescription(id):
    """Get a specific prescription"""
    current_user_id = int(get_jwt_identity())
    
    prescription = Prescription.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    return jsonify(prescription.to_dict()), 200

@prescriptions_bp.route('', methods=['POST'])
@jwt_required()
def create_prescription():
    """Create a new prescription"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    prescription = Prescription(
        user_id=current_user_id,
        doctor_id=data.get('doctor_id'),
        medication_id=data.get('medication_id'),
        prescription_number=data.get('prescription_number'),
        prescribed_date=data.get('prescribed_date'),
        expiry_date=data.get('expiry_date'),
        dosage=data.get('dosage'),
        frequency=data.get('frequency'),
        quantity=data.get('quantity'),
        refills_remaining=data.get('refills_remaining'),
        instructions=data.get('instructions'),
        status=data.get('status', 'active'),
        notes=data.get('notes')
    )
    
    db.session.add(prescription)
    db.session.commit()
    
    return jsonify({
        'message': 'Prescription created successfully',
        'prescription': prescription.to_dict()
    }), 201

@prescriptions_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_prescription(id):
    """Update a prescription"""
    current_user_id = int(get_jwt_identity())
    
    prescription = Prescription.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'doctor_id' in data:
        prescription.doctor_id = data['doctor_id']
    if 'medication_id' in data:
        prescription.medication_id = data['medication_id']
    if 'prescription_number' in data:
        prescription.prescription_number = data['prescription_number']
    if 'prescribed_date' in data:
        prescription.prescribed_date = data['prescribed_date']
    if 'expiry_date' in data:
        prescription.expiry_date = data['expiry_date']
    if 'dosage' in data:
        prescription.dosage = data['dosage']
    if 'frequency' in data:
        prescription.frequency = data['frequency']
    if 'quantity' in data:
        prescription.quantity = data['quantity']
    if 'refills_remaining' in data:
        prescription.refills_remaining = data['refills_remaining']
    if 'instructions' in data:
        prescription.instructions = data['instructions']
    if 'status' in data:
        prescription.status = data['status']
    if 'notes' in data:
        prescription.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Prescription updated successfully',
        'prescription': prescription.to_dict()
    }), 200

@prescriptions_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_prescription(id):
    """Delete a prescription"""
    current_user_id = int(get_jwt_identity())
    
    prescription = Prescription.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(prescription)
    db.session.commit()
    
    return jsonify({'message': 'Prescription deleted successfully'}), 200
