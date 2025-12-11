import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MsgBoard.settings')

app = Celery('MsgBoard')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.update(
    CELERY_TIMEZONE = 'UTC',
    CELERY_POOL='solo',
)

app.conf.beat_schedule = {
    'weekly-mailing' : {
        'task': 'mboard.tasks.subscribers_notification_weekly',
        'schedule': crontab(hour = 8, minute=0, day_of_week='mon'),
        }
}