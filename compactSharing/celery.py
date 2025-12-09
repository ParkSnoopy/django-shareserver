from __future__ import absolute_import, unicode_literals
import sys
from kombu.utils import encoding
sys.modules['celery.utils.encoding'] = encoding

import os, django
from celery import Celery
from datetime import timedelta
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compactSharing.settings')

app = Celery('compactSharing', include=['compactSharing.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='UTC',
    CELERY_ENABLE_UTC=True,
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler',
)

django.setup()


app.autodiscover_tasks()
if __name__ == '__main__':
    app.start()
    