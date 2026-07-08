"""Celery application factory."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "leadforge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],  # auto-discover task modules
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,          # Ack only after task completes (safer)
    worker_prefetch_multiplier=1, # One task at a time per worker process
)
