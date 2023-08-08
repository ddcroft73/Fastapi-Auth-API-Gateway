
from celery import Task
from celery import Celery

from app.core import settings

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery_app.conf.timezone = 'US/Eastern'