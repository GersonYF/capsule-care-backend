from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime, timedelta
from models import Medication, UserMedication, MedicationIntake
from sqlalchemy import func

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
    
    # Validar criticidad si se proporciona
    valid_criticalities = ['low', 'medium', 'high', 'critical']
    criticality = data.get('criticality', 'medium')
    if criticality not in valid_criticalities:
        return jsonify({'error': f'Invalid criticality. Must be one of: {", ".join(valid_criticalities)}'}), 400
    
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
        requires_prescription=data.get('requires_prescription', True),
        criticality=criticality  # NUEVO
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
    
    # NUEVO: Actualizar criticidad con validación
    if 'criticality' in data:
        valid_criticalities = ['low', 'medium', 'high', 'critical']
        if data['criticality'] not in valid_criticalities:
            return jsonify({'error': f'Invalid criticality. Must be one of: {", ".join(valid_criticalities)}'}), 400
        medication.criticality = data['criticality']
    
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
    current_user_id = int(get_jwt_identity())
    
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
    current_user_id = int(get_jwt_identity())
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
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('custom_name'):
        return jsonify({'error': 'Medication name is required'}), 400
    
    medication_name = data['custom_name'].strip()
    medication_id = data.get('medication_id')
    
    if medication_id:
        medication = Medication.query.get(medication_id)
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
    else:
        medication = Medication.query.filter(
            db.func.lower(Medication.name) == medication_name.lower()
        ).filter_by(is_active=True).first()
        
        if not medication:
            criticality = data.get('criticality', 'medium')
            valid_criticalities = ['low', 'medium', 'high', 'critical']
            if criticality not in valid_criticalities:
                criticality = 'medium'
            
            medication = Medication(
                name=medication_name,
                strength=data.get('prescribed_dosage'),
                description=f"Medication added by user",
                requires_prescription=True,
                criticality=criticality
            )
            db.session.add(medication)
            db.session.flush()
    
    user_med = UserMedication(
        user_id=current_user_id,
        medication_id=medication.id,
        custom_name=data['custom_name'],
        prescribed_dosage=data.get('prescribed_dosage'),
        prescribed_frequency=data.get('prescribed_frequency'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        doctor_instructions=data.get('doctor_instructions'),
        notes=data.get('notes')
    )
    
    db.session.add(user_med)
    db.session.commit()
    
    result = user_med.to_dict()
    result['medication'] = medication.to_dict()
    
    return jsonify({
        'message': 'Medication added to user successfully',
        'user_medication': result,
        'medication_created': medication_id is None
    }), 201

@medications_bp.route('/user/<int:id>', methods=['PUT'])
@jwt_required()
def update_user_medication(id):
    """Update a user medication"""
    current_user_id = int(get_jwt_identity())
    user_med = UserMedication.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'medication_id' in data:
        # If updating medication_id, verify it exists (or is None)
        if data['medication_id'] is not None:
            medication = Medication.query.get(data['medication_id'])
            if not medication:
                return jsonify({'error': 'Medication not found'}), 404
        user_med.medication_id = data['medication_id']
    
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
    
    result = user_med.to_dict()
    if user_med.medication:
        result['medication'] = user_med.medication.to_dict()
    
    return jsonify({
        'message': 'User medication updated successfully',
        'user_medication': result
    }), 200

@medications_bp.route('/user/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user_medication(id):
    """Soft delete a user medication"""
    current_user_id = int(get_jwt_identity())
    user_med = UserMedication.query.filter_by(
        id=id,
        user_id=current_user_id
    ).first_or_404()
    
    user_med.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User medication deleted successfully'}), 200

@medications_bp.route('/user/metrics', methods=['GET'])
@jwt_required()
def get_user_medication_metrics():
    """Get user medication adherence metrics weighted by criticality"""
    current_user_id = int(get_jwt_identity())
    
    # Obtener rango de fechas (últimos 30 días por defecto)
    days = request.args.get('days', 30, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Obtener medicamentos activos del usuario con su criticidad
    user_meds = db.session.query(
        UserMedication,
        Medication
    ).join(
        Medication,
        UserMedication.medication_id == Medication.id
    ).filter(
        UserMedication.user_id == current_user_id,
        UserMedication.is_active == True
    ).all()
    
    if not user_meds:
        return jsonify({
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'overall_weighted_adherence': 0,
            'overall_simple_adherence': 0,
            'total_medications': 0,
            'total_taken': 0,
            'total_expected': 0,
            'total_missed_critical': 0,
            'medications': []
        }), 200
    
    def get_expected_doses_per_day(frequency):
        """Calculate expected doses per day from frequency string"""
        if not frequency:
            return 1
        
        freq_lower = frequency.lower().strip()
        
        if any(term in freq_lower for term in ['dos veces', '2 veces', 'twice']):
            return 2
        if any(term in freq_lower for term in ['tres veces', '3 veces', 'three times']):
            return 3
        if any(term in freq_lower for term in ['cuatro veces', '4 veces', 'four times']):
            return 4
        if 'cada 12 horas' in freq_lower or 'every 12 hours' in freq_lower:
            return 2
        if 'cada 8 horas' in freq_lower or 'every 8 hours' in freq_lower:
            return 3
        if 'cada 6 horas' in freq_lower or 'every 6 hours' in freq_lower:
            return 4
        
        return 1
    
    total_weight = 0
    total_weighted_taken = 0
    total_simple_taken = 0
    total_expected = 0
    total_missed_critical = 0
    medication_stats = []
    
    for user_med, medication in user_meds:
        weight = medication.get_criticality_weight()
        doses_per_day = get_expected_doses_per_day(user_med.prescribed_frequency)
        expected_total = doses_per_day * days
        
        # Obtener estadísticas de intake
        intakes = db.session.query(
            MedicationIntake.status,
            func.count(MedicationIntake.id).label('count')
        ).filter(
            MedicationIntake.user_medication_id == user_med.id,
            MedicationIntake.created_at >= start_date,
            MedicationIntake.created_at <= end_date
        ).group_by(MedicationIntake.status).all()
        
        taken = sum(i.count for i in intakes if i.status == 'taken')
        missed = sum(i.count for i in intakes if i.status == 'missed')
        skipped = sum(i.count for i in intakes if i.status == 'skipped')
        total_recorded = taken + missed + skipped
        
        # Usar el menor entre expected_total y total_recorded para evitar sobre-estimación
        effective_expected = min(expected_total, max(total_recorded, expected_total))
        
        simple_adherence = (taken / effective_expected * 100) if effective_expected > 0 else 0
        
        # Calcular pesos ponderados
        total_weight += weight * effective_expected
        total_weighted_taken += taken * weight
        total_simple_taken += taken
        total_expected += effective_expected
        
        # Contar dosis críticas perdidas
        if medication.criticality == 'critical':
            total_missed_critical += missed
        
        medication_stats.append({
            'medication_id': medication.id,
            'user_medication_id': user_med.id,
            'medication_name': medication.name,
            'custom_name': user_med.custom_name,
            'criticality': medication.criticality,
            'criticality_weight': weight,
            'doses_per_day': doses_per_day,
            'simple_adherence_rate': round(simple_adherence, 2),
            'taken': taken,
            'missed': missed,
            'skipped': skipped,
            'expected': effective_expected,
            'total_recorded': total_recorded
        })
    
    # Calcular adherencias generales
    overall_simple_adherence = (total_simple_taken / total_expected * 100) if total_expected > 0 else 0
    overall_weighted_adherence = (total_weighted_taken / total_weight) if total_weight > 0 else 0
    
    return jsonify({
        'period_days': days,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'overall_weighted_adherence': round(overall_weighted_adherence * 100, 2),
        'overall_simple_adherence': round(overall_simple_adherence, 2),
        'total_medications': len(user_meds),
        'total_taken': total_simple_taken,
        'total_expected': total_expected,
        'total_missed_critical': total_missed_critical,
        'medications': sorted(medication_stats, key=lambda x: x['criticality_weight'], reverse=True)
    }), 200


@medications_bp.route('/user/metrics/daily', methods=['GET'])
@jwt_required()
def get_daily_metrics():
    """Get daily metrics for the last N days"""
    current_user_id = int(get_jwt_identity())
    
    days = request.args.get('days', 7, type=int)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    
    # Obtener medicamentos activos del usuario
    user_meds = db.session.query(
        UserMedication,
        Medication
    ).join(
        Medication,
        UserMedication.medication_id == Medication.id
    ).filter(
        UserMedication.user_id == current_user_id,
        UserMedication.is_active == True
    ).all()
    
    if not user_meds:
        return jsonify({
            'days': [],
            'period_days': days
        }), 200
    
    def get_expected_doses_per_day(frequency):
        if not frequency:
            return 1
        
        freq_lower = frequency.lower().strip()
        
        if any(term in freq_lower for term in ['dos veces', '2 veces', 'twice']):
            return 2
        if any(term in freq_lower for term in ['tres veces', '3 veces', 'three times']):
            return 3
        if any(term in freq_lower for term in ['cuatro veces', '4 veces', 'four times']):
            return 4
        if 'cada 12 horas' in freq_lower or 'every 12 hours' in freq_lower:
            return 2
        if 'cada 8 horas' in freq_lower or 'every 8 hours' in freq_lower:
            return 3
        if 'cada 6 horas' in freq_lower or 'every 6 hours' in freq_lower:
            return 4
        
        return 1
    
    daily_metrics = []
    
    for day_offset in range(days):
        current_day = start_date + timedelta(days=day_offset)
        day_start = datetime.combine(current_day, datetime.min.time())
        day_end = datetime.combine(current_day, datetime.max.time())
        
        day_weight = 0
        day_weighted_taken = 0
        day_simple_taken = 0
        day_expected = 0
        day_missed_critical = 0
        
        for user_med, medication in user_meds:
            weight = medication.get_criticality_weight()
            doses_per_day = get_expected_doses_per_day(user_med.prescribed_frequency)
            
            # Obtener intakes del día
            day_intakes = db.session.query(
                MedicationIntake.status,
                func.count(MedicationIntake.id).label('count')
            ).filter(
                MedicationIntake.user_medication_id == user_med.id,
                MedicationIntake.status_at >= day_start,
                MedicationIntake.status_at <= day_end
            ).group_by(MedicationIntake.status).all()
            
            taken = sum(i.count for i in day_intakes if i.status == 'taken')
            missed = sum(i.count for i in day_intakes if i.status == 'missed')
            
            day_weight += weight * doses_per_day
            day_weighted_taken += taken * weight
            day_simple_taken += taken
            day_expected += doses_per_day
            
            if medication.criticality == 'critical':
                day_missed_critical += missed
        
        simple_adherence = (day_simple_taken / day_expected * 100) if day_expected > 0 else 0
        weighted_adherence = (day_weighted_taken / day_weight * 100) if day_weight > 0 else 0
        
        daily_metrics.append({
            'date': current_day.isoformat(),
            'taken_count': day_simple_taken,
            'expected_count': day_expected,
            'simple_adherence': round(simple_adherence, 2),
            'weighted_adherence': round(weighted_adherence, 2),
            'missed_critical': day_missed_critical,
            'is_compliant': weighted_adherence >= 80
        })
    
    return jsonify({
        'days': daily_metrics,
        'period_days': days
    }), 200
