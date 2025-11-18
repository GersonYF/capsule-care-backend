from datetime import datetime, timedelta
from api.extensions import db
from api.models import (
    Reminder, ReminderLog, Notification, UserMedication,
    User, Medication, EmergencyContact
)
from celery import shared_task
import logging


logger = logging.getLogger(__name__)


@shared_task(name='tasks.notification_tasks.check_and_send_reminders')
def check_and_send_reminders():
    """
    Verifica recordatorios activos y envía notificaciones para las próximas dosis
    """
    try:
        now = datetime.utcnow()
        current_time = now.time()
        current_date = now.date()
        
        reminders = Reminder.query.filter_by(
            is_active=True,
            event_enabled=True
        ).all()
        
        notifications_sent = 0
        
        for reminder in reminders:
            if reminder.start_date and current_date < reminder.start_date:
                continue
            if reminder.end_date and current_date > reminder.end_date:
                continue
            
            if should_send_reminder(reminder, current_time, current_date):
                existing_notification = Notification.query.filter_by(
                    user_id=reminder.user_medication.user_id,
                    reminder_id=reminder.id,
                    status='pending'
                ).filter(
                    Notification.scheduled_at >= now - timedelta(minutes=30),
                    Notification.scheduled_at <= now + timedelta(minutes=30)
                ).first()
                
                if not existing_notification:
                    send_reminder_notification.delay(reminder.id)
                    notifications_sent += 1
        
        logger.info(f"Checked reminders. Scheduled {notifications_sent} notifications.")
        return {'notifications_scheduled': notifications_sent}
        
    except Exception as e:
        logger.error(f"Error checking reminders: {str(e)}")
        return {'error': str(e)}


def should_send_reminder(reminder, current_time, current_date):
    if not reminder.reminder_time:
        return False
    
    reminder_minutes = reminder.reminder_time.hour * 60 + reminder.reminder_time.minute
    current_minutes = current_time.hour * 60 + current_time.minute
    
    if abs(reminder_minutes - current_minutes) > 1:
        return False
    
    if reminder.frequency_type == 'daily':
        return True
    
    if reminder.frequency_type == 'weekly':
        if reminder.time_of_week:
            days = [d.strip().lower() for d in reminder.time_of_week.split(',')]
            current_day = current_date.strftime('%A').lower()
            return current_day in days
        return False
    
    if reminder.frequency_type == 'monthly':
        if reminder.frequency_value:
            return current_date.day == reminder.frequency_value
        return False
    
    if reminder.frequency_type == 'custom':
        if reminder.start_date and reminder.frequency_value:
            days_diff = (current_date - reminder.start_date).days
            return days_diff % reminder.frequency_value == 0
        return False
    
    return False


@shared_task(name='tasks.notification_tasks.send_reminder_notification')
def send_reminder_notification(reminder_id):
    try:
        reminder = Reminder.query.get(reminder_id)
        if not reminder or not reminder.is_active:
            return {'error': 'Reminder not found or inactive'}
        
        user_med = reminder.user_medication
        medication = user_med.medication
        user = user_med.user
        
        now = datetime.utcnow()
        
        reminder_log = ReminderLog(
            reminder_id=reminder.id,
            scheduled_time=now,
            status='pending'
        )
        db.session.add(reminder_log)
        db.session.flush()
        
        notifications_created = []
        
        if reminder.push_notification:
            notification = Notification(
                user_id=user.id,
                reminder_id=reminder.id,
                notification_type='medication_reminder',
                title=f"💊 Recordatorio: {user_med.custom_name or medication.name}",
                message=f"Es hora de tomar tu medicamento: {user_med.prescribed_dosage or 'dosis prescrita'}",
                delivery_method='push',
                scheduled_at=now,
                status='pending'
            )
            db.session.add(notification)
            notifications_created.append('push')
        
        if reminder.email_notification and user.email:
            notification = Notification(
                user_id=user.id,
                reminder_id=reminder.id,
                notification_type='medication_reminder',
                title=f"Recordatorio: {user_med.custom_name or medication.name}",
                message=f"Es hora de tomar {user_med.prescribed_dosage or 'tu dosis prescrita'}.\n\nInstrucciones: {user_med.doctor_instructions or 'N/A'}",
                delivery_method='email',
                scheduled_at=now,
                status='pending'
            )
            db.session.add(notification)
            notifications_created.append('email')
        
        db.session.commit()
        
        for notification in Notification.query.filter_by(
            user_id=user.id,
            reminder_id=reminder.id,
            status='pending'
        ).all():
            send_notification.delay(notification.id)
        
        logger.info(f"Created notifications for reminder {reminder_id}: {notifications_created}")
        return {
            'reminder_id': reminder_id,
            'notifications_created': notifications_created
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending reminder notification: {str(e)}")
        return {'error': str(e)}


@shared_task(name='tasks.notification_tasks.send_notification')
def send_notification(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return {'error': 'Notification not found'}
        
        logger.info(f"Sending {notification.delivery_method} notification to user {notification.user_id}")
        
        notification.sent_at = datetime.utcnow()
        notification.status = 'sent'
        db.session.commit()
        
        return {
            'notification_id': notification_id,
            'status': 'sent',
            'method': notification.delivery_method
        }
        
    except Exception as e:
        if notification.retry_count < 3:
            notification.retry_count += 1
            notification.error_message = str(e)
            db.session.commit()
            
            send_notification.apply_async(
                args=[notification_id],
                countdown=300
            )
        else:
            notification.status = 'failed'
            notification.error_message = str(e)
            db.session.commit()
        
        logger.error(f"Error sending notification {notification_id}: {str(e)}")
        return {'error': str(e)}


@shared_task(name='tasks.notification_tasks.check_missed_doses')
def check_missed_doses():
    try:
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=30)
        
        missed_logs = ReminderLog.query.filter(
            ReminderLog.status == 'pending',
            ReminderLog.scheduled_time < cutoff_time
        ).all()
        
        notifications_sent = 0
        
        for log in missed_logs:
            log.status = 'missed'
            reminder = log.reminder
            user_med = reminder.user_medication
            medication = user_med.medication
            user = user_med.user
            
            notification = Notification(
                user_id=user.id,
                reminder_id=reminder.id,
                notification_type='missed_dose',
                title="⚠️ Dosis perdida",
                message=f"No has registrado la toma de {user_med.custom_name or medication.name}",
                delivery_method='push',
                scheduled_at=now,
                status='pending'
            )
            db.session.add(notification)
            
            if medication.criticality in ['high', 'critical']:
                emergency_contacts = EmergencyContact.query.filter_by(
                    user_id=user.id,
                    notify_missed_doses=True
                ).all()
                
                for contact in emergency_contacts:
                    if contact.email:
                        db.session.add(Notification(
                            user_id=user.id,
                            notification_type='emergency_alert',
                            title=f"Alerta: Dosis perdida - {user.first_name}",
                            message=f"{user.first_name} no ha tomado su medicamento {medication.name}",
                            delivery_method='email',
                            scheduled_at=now,
                            status='pending'
                        ))
            
            notifications_sent += 1
        
        db.session.commit()
        
        for notif in Notification.query.filter_by(status='pending').all():
            send_notification.delay(notif.id)
        
        logger.info(
            f"Checked missed doses. Found {len(missed_logs)} missed, sent {notifications_sent} alerts."
        )
        return {
            'missed_doses': len(missed_logs),
            'notifications_sent': notifications_sent
        }
        
    except Exception as e:
        logger.error(f"Error checking missed doses: {str(e)}")
        return {'error': str(e)}


@shared_task(name='tasks.notification_tasks.cleanup_old_notifications')
def cleanup_old_notifications():
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted_count = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.status == 'read'
        ).delete()
        
        old_logs = ReminderLog.query.filter(
            ReminderLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"Cleaned {deleted_count} notifications & {old_logs} logs")
        return {
            'notifications_deleted': deleted_count,
            'logs_deleted': old_logs
        }
        
    except Exception as e:
        logger.error(f"Error cleaning old data: {str(e)}")
        return {'error': str(e)}


@shared_task(name='tasks.notification_tasks.schedule_reminder')
def schedule_reminder(reminder_id, scheduled_datetime):
    send_reminder_notification.apply_async(
        args=[reminder_id],
        eta=scheduled_datetime
    )
    
    return {
        'reminder_id': reminder_id,
        'scheduled_for': scheduled_datetime.isoformat()
    }
