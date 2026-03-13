from celery import Celery

from app.config import settings

celery = Celery("cherrypick")

celery.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=settings.CELERY_CONCURRENCY,
    task_soft_time_limit=660,
    task_time_limit=720,
    task_routes={
        "app.tasks.download_trend.*": {"queue": "default"},
        "app.tasks.generate_image.*": {"queue": "generation"},
        "app.tasks.generate_video.*": {"queue": "generation"},
        "app.tasks.postprod.*": {"queue": "postprod"},
    },
)

celery.autodiscover_tasks(["app.tasks"])
