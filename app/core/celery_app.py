from celery import Celery

from app.core.config import CELERY_BROKER_URL

celery = Celery("task", broker=CELERY_BROKER_URL)

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL
)

celery_app.conf.update(task_track_started=True)
