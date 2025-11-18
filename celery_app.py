import os
from celery import Celery
from celery.schedules import crontab
from api.app import app

# Initialize Celery with new-style config keys
celery = Celery('medication_reminders')

# Set broker and result backend using new keys
celery.conf.broker_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
celery.conf.result_backend = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Additional configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Task context integration with Flask
class FlaskTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = FlaskTask

# Beat schedule
celery.conf.beat_schedule = {
    'check-and-send-reminders': {
        'task': 'tasks.notification_tasks.check_and_send_reminders',
        'schedule': 60.0,
    },
    'check-missed-doses': {
        'task': 'tasks.notification_tasks.check_missed_doses',
        'schedule': 300.0,
    },
    'cleanup-old-notifications': {
        'task': 'tasks.notification_tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),
    },
}

