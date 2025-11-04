-- Agregar columna reset_token
ALTER TABLE users 
ADD COLUMN reset_token VARCHAR(100) NULL UNIQUE;

-- Agregar columna reset_token_expiry
ALTER TABLE users 
ADD COLUMN reset_token_expiry TIMESTAMP NULL;

-- 1. Medicamentos (catálogo general)
INSERT INTO medications (id, name, generic_name, brand_name, description, manufacturer, dosage_form, strength, route_of_administration, uses, contraindications, storage_instructions, requires_prescription, is_active, created_at)
VALUES 
(3, 'Losartán', 'Losartan Potassium', 'Cozaar', 'Medicamento para controlar la presión arterial alta', 'Merck', 'Tableta', '50mg', 'Oral', 'Hipertensión arterial, protección renal en diabetes', 'Embarazo, hipersensibilidad al principio activo', 'Conservar a temperatura ambiente, proteger de la humedad', true, true, '2024-01-10 09:00:00'),
(4, 'Metformina', 'Metformin HCl', 'Glucophage', 'Antidiabético oral para diabetes tipo 2', 'Bristol-Myers Squibb', 'Tableta', '850mg', 'Oral', 'Diabetes mellitus tipo 2, síndrome de ovario poliquístico', 'Insuficiencia renal severa, acidosis metabólica', 'Conservar a temperatura ambiente', true, true, '2024-01-10 09:15:00'),
(5, 'Atorvastatina', 'Atorvastatin', 'Lipitor', 'Estatina para reducir el colesterol', 'Pfizer', 'Tableta', '20mg', 'Oral', 'Hipercolesterolemia, prevención de enfermedad cardiovascular', 'Enfermedad hepática activa, embarazo', 'Conservar a temperatura ambiente', true, true, '2024-01-10 09:30:00'),
(6, 'Omeprazol', 'Omeprazole', 'Prilosec', 'Inhibidor de la bomba de protones', 'AstraZeneca', 'Cápsula', '20mg', 'Oral', 'Úlcera gástrica, reflujo gastroesofágico, gastritis', 'Hipersensibilidad al principio activo', 'Conservar en lugar fresco y seco', false, true, '2024-01-10 09:45:00'),
(7, 'Aspirina', 'Acetylsalicylic Acid', 'Aspirin', 'Antiinflamatorio y antiagregante plaquetario', 'Bayer', 'Tableta', '100mg', 'Oral', 'Prevención de eventos cardiovasculares, dolor, fiebre', 'Úlcera péptica activa, trastornos de coagulación', 'Conservar a temperatura ambiente', false, true, '2024-01-10 10:00:00');

-- 2. Doctores
INSERT INTO doctors (id, first_name, last_name, specialty, license_number, phone, email, address, is_active, created_at)
VALUES 
(1, 'Carlos', 'Rodríguez', 'Medicina Interna', 'MED-12345-COL', '+57-300-9876543', 'dr.rodriguez@hospital.com', 'Hospital Universitario del Valle, Cali, Colombia', true, '2024-01-10 08:00:00'),
(2, 'Ana', 'Martínez', 'Endocrinología', 'MED-67890-COL', '+57-301-1122334', 'dra.martinez@clinica.com', 'Clínica Imbanaco, Cali, Colombia', true, '2024-01-10 08:30:00'),
(3, 'Luis', 'Gómez', 'Cardiología', 'MED-54321-COL', '+57-302-5566778', 'dr.gomez@cardio.com', 'Centro Cardiovascular del Valle, Cali, Colombia', true, '2024-01-10 09:00:00');

-- 3. Relación Usuario-Doctor
INSERT INTO user_doctors (user_id, doctor_id, relationship_type, is_primary, relationship_start_date, created_at)
VALUES 
(2, 1, 'primary', true, '2024-01-15', '2024-01-15 10:30:00'),
(2, 2, 'specialist', false, '2024-02-01', '2024-02-01 11:00:00'),
(2, 3, 'specialist', false, '2024-03-10', '2024-03-10 14:30:00');

-- 4. Medicamentos del Usuario (sin especificar ID para que se autogeneren)
INSERT INTO user_medications (user_id, medication_id, custom_name, prescribed_dosage, prescribed_frequency, start_date, doctor_instructions, is_active, created_at)
VALUES 
(2, 3, 'Losartán para presión', '50mg', 'Una vez al día', '2024-02-01', 'Tomar en ayunas, preferiblemente en la mañana', true, '2024-02-01 10:00:00'),
(2, 4, 'Metformina diabetes', '850mg', 'Dos veces al día', '2024-02-01', 'Tomar con las comidas (desayuno y cena)', true, '2024-02-01 10:15:00'),
(2, 5, 'Atorvastatina colesterol', '20mg', 'Una vez al día', '2024-03-10', 'Tomar en la noche antes de dormir', true, '2024-03-10 15:00:00'),
(2, 6, 'Omeprazol gastritis', '20mg', 'Una vez al día', '2024-04-05', 'Tomar 30 minutos antes del desayuno', true, '2024-04-05 09:00:00'),
(2, 7, 'Aspirina protección cardíaca', '100mg', 'Una vez al día', '2024-03-10', 'Tomar después del desayuno con alimentos', true, '2024-03-10 15:15:00');

-- 5. Prescripciones
INSERT INTO prescriptions (user_id, doctor_id, medication_id, prescription_number, prescribed_date, expiry_date, dosage, frequency, quantity, refills_remaining, instructions, status, created_at)
VALUES 
(2, 2, 3, 'RX-2024-001', '2024-02-01', '2025-02-01', '50mg', 'Una vez al día', 30, 3, 'Control mensual de presión arterial', 'active', '2024-02-01 10:00:00'),
(2, 2, 4, 'RX-2024-002', '2024-02-01', '2025-02-01', '850mg', 'Dos veces al día', 60, 3, 'Control de glucemia cada 3 meses', 'active', '2024-02-01 10:15:00'),
(2, 3, 5, 'RX-2024-003', '2024-03-10', '2025-03-10', '20mg', 'Una vez al día', 30, 2, 'Perfil lipídico cada 6 meses', 'active', '2024-03-10 15:00:00'),
(2, 1, 6, 'RX-2024-004', '2024-04-05', '2025-04-05', '20mg', 'Una vez al día', 30, 5, 'Tomar según necesidad', 'active', '2024-04-05 09:00:00'),
(2, 3, 7, 'RX-2024-005', '2024-03-10', '2025-03-10', '100mg', 'Una vez al día', 30, 3, 'No suspender sin consultar', 'active', '2024-03-10 15:15:00');

-- NOTA: Para los siguientes inserts, primero necesitas obtener los IDs autogenerados de user_medications
-- Puedes ejecutar: SELECT id FROM user_medications WHERE user_id = 2 ORDER BY id;
-- Y reemplazar los valores en las siguientes consultas

-- 6. Recordatorios (ajusta los user_medication_id según los IDs reales generados)
-- Suponiendo que los IDs generados son del 3 al 7, ajusta según sea necesario:
INSERT INTO reminders (user_medication_id, title, description, reminder_time, frequency_type, frequency_value, start_date, is_active, push_notification, email_notification, created_at)
VALUES 
(3, 'Tomar Losartán', 'Medicamento para presión arterial', '08:00:00', 'daily', 1, '2024-02-01', true, true, false, '2024-02-01 10:00:00'),
(4, 'Tomar Metformina - Desayuno', 'Con el desayuno', '08:30:00', 'daily', 1, '2024-02-01', true, true, false, '2024-02-01 10:15:00'),
(4, 'Tomar Metformina - Cena', 'Con la cena', '19:30:00', 'daily', 1, '2024-02-01', true, true, false, '2024-02-01 10:16:00'),
(5, 'Tomar Atorvastatina', 'Medicamento para colesterol', '21:00:00', 'daily', 1, '2024-03-10', true, true, false, '2024-03-10 15:00:00'),
(6, 'Tomar Omeprazol', 'Antes del desayuno', '07:30:00', 'daily', 1, '2024-04-05', true, true, false, '2024-04-05 09:00:00'),
(7, 'Tomar Aspirina', 'Después del desayuno', '09:00:00', 'daily', 1, '2024-03-10', true, true, false, '2024-03-10 15:15:00');

-- 7. Contactos de Emergencia
INSERT INTO emergency_contacts (user_id, name, relationship, phone, email, is_primary, notify_missed_doses, created_at)
VALUES 
(2, 'Pedro García', 'Esposo', '+57-300-1111222', 'pedro.garcia@email.com', true, true, '2024-01-15 10:30:00'),
(2, 'Sofia García López', 'Hija', '+57-301-3333444', 'sofia.garcia@email.com', false, false, '2024-01-15 10:35:00'),
(2, 'Carmen López', 'Madre', '+57-302-5555666', 'carmen.lopez@email.com', false, true, '2024-01-15 10:40:00');

-- 8. Configuraciones de Usuario
INSERT INTO user_settings (user_id, setting_key, setting_value, data_type, description, created_at)
VALUES 
(2, 'notification_sound', 'true', 'boolean', 'Activar sonido en notificaciones', '2024-01-15 10:30:00'),
(2, 'reminder_advance_time', '15', 'integer', 'Minutos de anticipación para recordatorios', '2024-01-15 10:30:00'),
(2, 'theme', 'light', 'string', 'Tema de la aplicación', '2024-01-15 10:30:00'),
(2, 'language', 'es', 'string', 'Idioma de la aplicación', '2024-01-15 10:30:00'),
(2, 'timezone', 'America/Bogota', 'string', 'Zona horaria', '2024-01-15 10:30:00');

-- 9. Logs de Actividad
INSERT INTO activity_logs (user_id, entity_type, entity_id, action, description, ip_address, created_at)
VALUES 
(2, 'user', 2, 'login', 'Inicio de sesión exitoso', '192.168.1.100', '2024-11-03 08:00:00'),
(2, 'medication_intake', 3, 'create', 'Registro de toma de medicamento', '192.168.1.100', '2024-11-03 08:05:00'),
(2, 'reminder', 3, 'acknowledge', 'Recordatorio confirmado', '192.168.1.100', '2024-11-03 08:05:00'),
(2, 'user_medication', 3, 'view', 'Consulta de información de medicamento', '192.168.1.100', '2024-11-03 09:30:00'),
(2, 'prescription', 1, 'view', 'Consulta de prescripción', '192.168.1.100', '2024-11-03 10:00:00');

-- DATOS CORREGIDOS PARA 2025
-- Asumiendo que user_medication_ids son 3, 4, 5, 6, 7

-- =================================================
-- DÍA 1: 2025-10-28 (hace 6 días desde 3 nov 2025)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(3, '2025-10-28 08:10:00', '50mg', 'taken', 'Todo normal', '2025-10-28 08:10:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-28 08:35:00', '850mg', 'taken', '2025-10-28 08:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-28 19:45:00', '850mg', 'taken', '2025-10-28 19:45:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(5, '2025-10-28 21:05:00', '20mg', 'taken', '2025-10-28 21:05:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-10-28 07:35:00', '20mg', 'taken', '2025-10-28 07:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-10-28 09:15:00', '100mg', 'taken', '2025-10-28 09:15:00');

-- =================================================
-- DÍA 2: 2025-10-29 (hace 5 días)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-10-29 08:05:00', '50mg', 'taken', '2025-10-29 08:05:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-29 08:32:00', '850mg', 'taken', '2025-10-29 08:32:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(4, '2025-10-29 19:30:00', NULL, 'missed', 'Olvidé tomar la dosis', '2025-10-29 20:30:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(5, '2025-10-29 21:10:00', '20mg', 'taken', '2025-10-29 21:10:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-10-29 07:40:00', '20mg', 'taken', '2025-10-29 07:40:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-10-29 09:05:00', '100mg', 'taken', '2025-10-29 09:05:00');

-- =================================================
-- DÍA 3: 2025-10-30 (hace 4 días)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-10-30 08:08:00', '50mg', 'taken', '2025-10-30 08:08:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-30 08:40:00', '850mg', 'taken', '2025-10-30 08:40:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-30 19:35:00', '850mg', 'taken', '2025-10-30 19:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(5, '2025-10-30 21:00:00', '20mg', 'taken', '2025-10-30 21:00:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-10-30 07:32:00', '20mg', 'taken', '2025-10-30 07:32:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(7, '2025-10-30 09:20:00', '100mg', 'taken', 'Tomada con el desayuno', '2025-10-30 09:20:00');

-- =================================================
-- DÍA 4: 2025-10-31 (hace 3 días)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-10-31 08:03:00', '50mg', 'taken', '2025-10-31 08:03:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-31 08:33:00', '850mg', 'taken', '2025-10-31 08:33:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-31 19:50:00', '850mg', 'taken', '2025-10-31 19:50:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(5, '2025-10-31 21:00:00', NULL, 'missed', 'Dormí temprano y olvidé tomarla', '2025-10-31 22:30:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-10-31 07:35:00', '20mg', 'taken', '2025-10-31 07:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-10-31 09:10:00', '100mg', 'taken', '2025-10-31 09:10:00');

-- =================================================
-- DÍA 5: 2025-11-01 (hace 2 días)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-11-01 08:15:00', '50mg', 'taken', '2025-11-01 08:15:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-11-01 08:30:00', '850mg', 'taken', '2025-11-01 08:30:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-11-01 19:32:00', '850mg', 'taken', '2025-11-01 19:32:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(5, '2025-11-01 21:05:00', '20mg', 'taken', '2025-11-01 21:05:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-11-01 07:38:00', '20mg', 'taken', '2025-11-01 07:38:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-11-01 09:05:00', '100mg', 'taken', '2025-11-01 09:05:00');

-- =================================================
-- DÍA 6: 2025-11-02 (ayer)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(3, '2025-11-02 08:00:00', NULL, 'missed', 'Salí temprano y se me olvidó', '2025-11-02 10:00:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(4, '2025-11-02 09:15:00', '850mg', 'taken', 'Tomada tarde', '2025-11-02 09:15:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-11-02 19:35:00', '850mg', 'taken', '2025-11-02 19:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(5, '2025-11-02 21:02:00', '20mg', 'taken', '2025-11-02 21:02:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-11-02 07:33:00', '20mg', 'taken', '2025-11-02 07:33:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-11-02 09:08:00', '100mg', 'taken', '2025-11-02 09:08:00');

-- =================================================
-- DÍA 7: 2025-11-03 (hoy)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-11-03 08:05:00', '50mg', 'taken', '2025-11-03 08:05:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-11-03 08:32:00', '850mg', 'taken', '2025-11-03 08:32:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(6, '2025-11-03 07:35:00', '20mg', 'taken', '2025-11-03 07:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(7, '2025-11-03 09:10:00', '100mg', 'taken', '2025-11-03 09:10:00');

-- =================================================
-- DÍAS ANTERIORES (para más historial)
-- =================================================
INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(3, '2025-10-21 08:05:00', '50mg', 'taken', '2025-10-21 08:05:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-21 08:35:00', '850mg', 'taken', '2025-10-21 08:35:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-21 19:40:00', '850mg', 'taken', '2025-10-21 19:40:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, notes, created_at) VALUES 
(3, '2025-10-14 08:00:00', NULL, 'missed', 'Estaba de viaje', '2025-10-14 10:00:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-14 08:45:00', '850mg', 'taken', '2025-10-14 08:45:00');

INSERT INTO medication_intake (user_medication_id, status_at, dosage_taken, status, created_at) VALUES 
(4, '2025-10-14 19:30:00', '850mg', 'taken', '2025-10-14 19:30:00');


-- NOTIFICACIONES PARA EL USER_ID 2
-- Asumiendo que los reminder_ids son del 1 al 6

-- =================================================
-- NOTIFICACIONES DE HOY (2025-11-03) - ENVIADAS Y LEÍDAS
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 5, 'medication_reminder', 'Hora de tomar Omeprazol', 'Recuerda tomar tu Omeprazol antes del desayuno', 'push', '2025-11-03 07:30:00', '2025-11-03 07:30:00', '2025-11-03 07:35:00', 'read', '2025-11-03 07:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 1, 'medication_reminder', 'Hora de tomar Losartán', 'Es hora de tomar tu medicamento para la presión arterial', 'push', '2025-11-03 08:00:00', '2025-11-03 08:00:00', '2025-11-03 08:05:00', 'read', '2025-11-03 07:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-11-03 08:30:00', '2025-11-03 08:30:00', '2025-11-03 08:32:00', 'read', '2025-11-03 08:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 6, 'medication_reminder', 'Hora de tomar Aspirina', 'Recuerda tomar tu Aspirina después del desayuno', 'push', '2025-11-03 09:00:00', '2025-11-03 09:00:00', '2025-11-03 09:10:00', 'read', '2025-11-03 08:55:00');

-- NOTIFICACIONES PENDIENTES DE HOY
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 3, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con la cena', 'push', '2025-11-03 19:30:00', NULL, 'pending', '2025-11-03 19:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 4, 'medication_reminder', 'Hora de tomar Atorvastatina', 'Es hora de tu medicamento para el colesterol', 'push', '2025-11-03 21:00:00', NULL, 'pending', '2025-11-03 20:55:00');

-- =================================================
-- NOTIFICACIONES DE AYER (2025-11-02)
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 5, 'medication_reminder', 'Hora de tomar Omeprazol', 'Recuerda tomar tu Omeprazol antes del desayuno', 'push', '2025-11-02 07:30:00', '2025-11-02 07:30:00', '2025-11-02 07:33:00', 'read', '2025-11-02 07:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 1, 'medication_reminder', 'Hora de tomar Losartán', 'Es hora de tomar tu medicamento para la presión arterial', 'push', '2025-11-02 08:00:00', '2025-11-02 08:00:00', 'read', '2025-11-02 07:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-11-02 08:30:00', '2025-11-02 08:30:00', '2025-11-02 09:15:00', 'read', '2025-11-02 08:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 6, 'medication_reminder', 'Hora de tomar Aspirina', 'Recuerda tomar tu Aspirina después del desayuno', 'push', '2025-11-02 09:00:00', '2025-11-02 09:00:00', '2025-11-02 09:08:00', 'read', '2025-11-02 08:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 3, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con la cena', 'push', '2025-11-02 19:30:00', '2025-11-02 19:30:00', '2025-11-02 19:35:00', 'read', '2025-11-02 19:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 4, 'medication_reminder', 'Hora de tomar Atorvastatina', 'Es hora de tu medicamento para el colesterol', 'push', '2025-11-02 21:00:00', '2025-11-02 21:00:00', '2025-11-02 21:02:00', 'read', '2025-11-02 20:55:00');

-- =================================================
-- NOTIFICACIONES DE 2025-11-01
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 5, 'medication_reminder', 'Hora de tomar Omeprazol', 'Recuerda tomar tu Omeprazol antes del desayuno', 'push', '2025-11-01 07:30:00', '2025-11-01 07:30:00', '2025-11-01 07:38:00', 'read', '2025-11-01 07:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 1, 'medication_reminder', 'Hora de tomar Losartán', 'Es hora de tomar tu medicamento para la presión arterial', 'push', '2025-11-01 08:00:00', '2025-11-01 08:00:00', '2025-11-01 08:15:00', 'read', '2025-11-01 07:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-11-01 08:30:00', '2025-11-01 08:30:00', '2025-11-01 08:30:00', 'read', '2025-11-01 08:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 6, 'medication_reminder', 'Hora de tomar Aspirina', 'Recuerda tomar tu Aspirina después del desayuno', 'push', '2025-11-01 09:00:00', '2025-11-01 09:00:00', '2025-11-01 09:05:00', 'read', '2025-11-01 08:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 3, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con la cena', 'push', '2025-11-01 19:30:00', '2025-11-01 19:30:00', '2025-11-01 19:32:00', 'read', '2025-11-01 19:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 4, 'medication_reminder', 'Hora de tomar Atorvastatina', 'Es hora de tu medicamento para el colesterol', 'push', '2025-11-01 21:00:00', '2025-11-01 21:00:00', '2025-11-01 21:05:00', 'read', '2025-11-01 20:55:00');

-- =================================================
-- NOTIFICACIONES DE 2025-10-31
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 5, 'medication_reminder', 'Hora de tomar Omeprazol', 'Recuerda tomar tu Omeprazol antes del desayuno', 'push', '2025-10-31 07:30:00', '2025-10-31 07:30:00', '2025-10-31 07:35:00', 'read', '2025-10-31 07:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 1, 'medication_reminder', 'Hora de tomar Losartán', 'Es hora de tomar tu medicamento para la presión arterial', 'push', '2025-10-31 08:00:00', '2025-10-31 08:00:00', '2025-10-31 08:03:00', 'read', '2025-10-31 07:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-10-31 08:30:00', '2025-10-31 08:30:00', '2025-10-31 08:33:00', 'read', '2025-10-31 08:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 6, 'medication_reminder', 'Hora de tomar Aspirina', 'Recuerda tomar tu Aspirina después del desayuno', 'push', '2025-10-31 09:00:00', '2025-10-31 09:00:00', '2025-10-31 09:10:00', 'read', '2025-10-31 08:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 3, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con la cena', 'push', '2025-10-31 19:30:00', '2025-10-31 19:30:00', '2025-10-31 19:50:00', 'read', '2025-10-31 19:25:00');

-- Notificación no leída (missed)
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 4, 'medication_reminder', 'Hora de tomar Atorvastatina', 'Es hora de tu medicamento para el colesterol', 'push', '2025-10-31 21:00:00', '2025-10-31 21:00:00', 'sent', '2025-10-31 20:55:00');

-- =================================================
-- NOTIFICACIONES DE 2025-10-30
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 5, 'medication_reminder', 'Hora de tomar Omeprazol', 'Recuerda tomar tu Omeprazol antes del desayuno', 'push', '2025-10-30 07:30:00', '2025-10-30 07:30:00', '2025-10-30 07:32:00', 'read', '2025-10-30 07:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 1, 'medication_reminder', 'Hora de tomar Losartán', 'Es hora de tomar tu medicamento para la presión arterial', 'push', '2025-10-30 08:00:00', '2025-10-30 08:00:00', '2025-10-30 08:08:00', 'read', '2025-10-30 07:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-10-30 08:30:00', '2025-10-30 08:30:00', '2025-10-30 08:40:00', 'read', '2025-10-30 08:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 6, 'medication_reminder', 'Hora de tomar Aspirina', 'Recuerda tomar tu Aspirina después del desayuno', 'push', '2025-10-30 09:00:00', '2025-10-30 09:00:00', '2025-10-30 09:20:00', 'read', '2025-10-30 08:55:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 3, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con la cena', 'push', '2025-10-30 19:30:00', '2025-10-30 19:30:00', '2025-10-30 19:35:00', 'read', '2025-10-30 19:25:00');

INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 4, 'medication_reminder', 'Hora de tomar Atorvastatina', 'Es hora de tu medicamento para el colesterol', 'push', '2025-10-30 21:00:00', '2025-10-30 21:00:00', '2025-10-30 21:00:00', 'read', '2025-10-30 20:55:00');

-- =================================================
-- NOTIFICACIONES FALLIDAS (ejemplos)
-- =================================================
INSERT INTO notifications (user_id, reminder_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, retry_count, error_message, created_at) VALUES 
(2, 2, 'medication_reminder', 'Hora de tomar Metformina', 'Recuerda tomar tu Metformina con el desayuno', 'push', '2025-10-29 08:30:00', '2025-10-29 08:30:00', 'failed', 3, 'Device token invalid', '2025-10-29 08:25:00');

-- =================================================
-- NOTIFICACIONES DE TIPO SISTEMA
-- =================================================
INSERT INTO notifications (user_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 'system', 'Bienvenido a CapsuleCare', 'Gracias por usar nuestra aplicación para gestionar tus medicamentos', 'push', '2025-10-01 10:00:00', '2025-10-01 10:00:00', 'sent', '2025-10-01 09:55:00');

INSERT INTO notifications (user_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, read_at, status, created_at) VALUES 
(2, 'reminder_summary', 'Resumen semanal', 'Has tomado 35 de 42 dosis esta semana (83% de adherencia)', 'push', '2025-10-28 09:00:00', '2025-10-28 09:00:00', '2025-10-28 09:15:00', 'read', '2025-10-28 08:55:00');

INSERT INTO notifications (user_id, notification_type, title, message, delivery_method, scheduled_at, sent_at, status, created_at) VALUES 
(2, 'medication_refill', 'Recarga de medicamento', 'Tu Metformina tiene solo 5 días de inventario restante', 'push', '2025-10-25 10:00:00', '2025-10-25 10:00:00', 'sent', '2025-10-25 09:55:00');