# Skill: Celery + Redis

## Setup (celery_app.py)
```python
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
```

## Pattern d'une task
```python
import logging
from app.celery_app import celery
from app.database import supabase

logger = logging.getLogger(__name__)

@celery.task(bind=True, name="app.tasks.generate_image", max_retries=1, default_retry_delay=15)
def generate_image(self, job_id: str, persona_id: str, image_variation: int | None = None):
    logger.info("Starting", extra={"job_id": job_id})
    try:
        # 1. Update job status
        supabase.table("jobs").update({"status": "running", "current_step": "image_ready"}).eq("id", job_id).execute()
        
        # 2. Charger persona
        persona = supabase.table("personas").select("*").eq("id", persona_id).single().execute().data
        
        # 3. Appeler le service
        from app.services.fal_client import FalClient
        client = FalClient()
        result = client.generate_image(prompt=persona["prompt_image_base"])
        
        # 4. Upload + update job
        # ...
        
    except Exception as exc:
        supabase.table("jobs").update({"status": "failed", "error_message": str(exc)}).eq("id", job_id).execute()
        logger.error("Failed", extra={"job_id": job_id, "error": str(exc)})
        raise self.retry(exc=exc)
```

## Chain (pipeline)
```python
from celery import chain

def run_pipeline(job_id, persona_id, trend_source, trend_url, trend_storage_path, image_variation, video_duration, hook_text, font_override):
    task_chain = chain(
        download_trend.s(job_id, trend_source, trend_url, trend_storage_path),
        generate_image.s(job_id, persona_id, image_variation),
        generate_video.s(job_id, persona_id, video_duration),
        postprod.s(job_id, persona_id, hook_text, font_override),
    )
    result = task_chain.apply_async()
    return result.id
```

## Règles
- Toujours `bind=True` (accès à `self` pour retry)
- Toujours update le job status en DB au début ET à la fin
- Toujours try/except avec update status=failed
- Les tasks ne retournent PAS de gros objets — elles stockent dans Supabase et passent des IDs
- Chaque task reçoit `job_id` pour tracer
