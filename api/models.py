from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender_enum'))
    language = db.Column(db.String(10), default='en')
    profile_image_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    medications = db.relationship('UserMedication', back_populates='user', cascade='all, delete-orphan')
    doctors = db.relationship('UserDoctor', back_populates='user', cascade='all, delete-orphan')
    settings = db.relationship('UserSetting', back_populates='user', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', back_populates='user', cascade='all, delete-orphan')
    emergency_contacts = db.relationship('EmergencyContact', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'language': self.language,
            'profile_image_url': self.profile_image_url,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200))
    brand_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(200))
    dosage_form = db.Column(db.String(100))
    strength = db.Column(db.String(100))
    route_of_administration = db.Column(db.String(100))
    uses = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    storage_instructions = db.Column(db.Text)
    barcode = db.Column(db.String(100))
    image_url = db.Column(db.Text)
    requires_prescription = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_medications = db.relationship('UserMedication', back_populates='medication', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'generic_name': self.generic_name,
            'brand_name': self.brand_name,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'dosage_form': self.dosage_form,
            'strength': self.strength,
            'route_of_administration': self.route_of_administration,
            'uses': self.uses,
            'contraindications': self.contraindications,
            'storage_instructions': self.storage_instructions,
            'barcode': self.barcode,
            'image_url': self.image_url,
            'requires_prescription': self.requires_prescription,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    license_number = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_doctors = db.relationship('UserDoctor', back_populates='doctor', cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', back_populates='doctor', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialty': self.specialty,
            'license_number': self.license_number,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserMedication(db.Model):
    __tablename__ = 'user_medications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    custom_name = db.Column(db.String(200))
    prescribed_dosage = db.Column(db.String(100))
    prescribed_frequency = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    doctor_instructions = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='medications')
    medication = db.relationship('Medication', back_populates='user_medications')
    reminders = db.relationship('Reminder', back_populates='user_medication', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'medication_id': self.medication_id,
            'custom_name': self.custom_name,
            'prescribed_dosage': self.prescribed_dosage,
            'prescribed_frequency': self.prescribed_frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'doctor_instructions': self.doctor_instructions,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserDoctor(db.Model):
    __tablename__ = 'user_doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    relationship_type = db.Column(db.Enum('primary', 'specialist', 'other', name='relationship_type_enum'))
    is_primary = db.Column(db.Boolean, default=False)
    relationship_start_date = db.Column(db.Date)
    relationship_end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='doctors')
    doctor = db.relationship('Doctor', back_populates='user_doctors')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'relationship_type': self.relationship_type,
            'is_primary': self.is_primary,
            'relationship_start_date': self.relationship_start_date.isoformat() if self.relationship_start_date else None,
            'relationship_end_date': self.relationship_end_date.isoformat() if self.relationship_end_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'))
    prescription_number = db.Column(db.String(100))
    prescribed_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    refills_remaining = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'expired', 'cancelled', name='prescription_status_enum'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('Doctor', back_populates='prescriptions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'medication_id': self.medication_id,
            'prescription_number': self.prescription_number,
            'prescribed_date': self.prescribed_date.isoformat() if self.prescribed_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'quantity': self.quantity,
            'refills_remaining': self.refills_remaining,
            'instructions': self.instructions,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_medication_id = db.Column(db.Integer, db.ForeignKey('user_medications.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    reminder_time = db.Column(db.Time)
    time_of_week = db.Column(db.String(50))
    frequency_type = db.Column(db.Enum('daily', 'weekly', 'monthly', 'custom', name='frequency_type_enum'))
    frequency_value = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    event_enabled = db.Column(db.Boolean, default=True)
    calendar_reminder = db.Column(db.Boolean, default=False)
    push_notification = db.Column(db.Boolean, default=True)
    email_notification = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_medication = db.relationship('UserMedication', back_populates='reminders')
    reminder_logs = db.relationship('ReminderLog', back_populates='reminder', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_medication_id': self.user_medication_id,
            'title': self.title,
            'description': self.description,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'time_of_week': self.time_of_week,
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'event_enabled': self.event_enabled,
            'calendar_reminder': self.calendar_reminder,
            'push_notification': self.push_notification,
            'email_notification': self.email_notification,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ReminderLog(db.Model):
    __tablename__ = 'reminder_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminders.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('pending', 'sent', 'acknowledged', 'missed', name='reminder_status_enum'))
    notes = db.Column(db.Text)
    log_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reminder = db.relationship('Reminder', back_populates='reminder_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'reminder_id': self.reminder_id,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'actual_time': self.actual_time.isoformat() if self.actual_time else None,
            'status': self.status,
            'notes': self.notes,
            'log_metadata': self.log_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MediaFile(db.Model):
    __tablename__ = 'media_files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_entity_id = db.Column(db.Integer)
    related_entity_type = db.Column(db.String(50))
    original_name = db.Column(db.String(255))
    file_path = db.Column(db.Text)
    file_type = db.Column(db.String(50))
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.BigInteger)
    file_metadata = db.Column(db.JSON)
    description = db.Column(db.Text)
    is_processed = db.Column(db.Boolean, default=False)
    ai_analysis_result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type,
            'original_name': self.original_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_metadata': self.file_metadata,
            'description': self.description,
            'is_processed': self.is_processed,
            'ai_analysis_result': self.ai_analysis_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserSetting(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text)
    data_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'data_type': self.data_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    action = db.Column(db.String(50))
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='activity_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'old_data': self.old_data,
            'new_data': self.new_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    relationship = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_primary = db.Column(db.Boolean, default=False)
    notify_missed_doses = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='emergency_contacts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'relationship': self.relationship,
            'phone': self.phone,
            'email': self.email,
            'is_primary': self.is_primary,
            'notify_missed_doses': self.notify_missed_doses,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminders.id'))
    notification_type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    delivery_method = db.Column(db.Enum('push', 'email', 'sms', name='delivery_method_enum'))
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('pending', 'sent', 'failed', 'read', name='notification_status_enum'))
    retry_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reminder_id': self.reminder_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'delivery_method': self.delivery_method,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'status': self.status,
            'retry_count': self.retry_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MedicationIntake(db.Model):
    __tablename__ = 'medication_intake'
    
    id = db.Column(db.Integer, primary_key=True)
    user_medication_id = db.Column(db.Integer, db.ForeignKey('user_medications.id'), nullable=False)
    reminder_log_id = db.Column(db.Integer, db.ForeignKey('reminder_logs.id'))
    status_at = db.Column(db.DateTime)
    dosage_taken = db.Column(db.String(100))
    status = db.Column(db.Enum('taken', 'missed', 'skipped', name='intake_status_enum'))
    notes = db.Column(db.Text)
    side_effects_reported = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_medication_id': self.user_medication_id,
            'reminder_log_id': self.reminder_log_id,
            'status_at': self.status_at.isoformat() if self.status_at else None,
            'dosage_taken': self.dosage_taken,
            'status': self.status,
            'notes': self.notes,
            'side_effects_reported': self.side_effects_reported,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
