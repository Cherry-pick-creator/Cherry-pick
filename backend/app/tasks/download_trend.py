import logging

from app.celery_app import celery
from app.database import supabase
from app.services.downloader import Downloader
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    name="app.tasks.download_trend",
    max_retries=1,
    default_retry_delay=10,
    soft_time_limit=55,
    time_limit=60,
)
def download_trend(
    self,
    job_id: str,
    trend_source: str,
    trend_url: str | None = None,
    trend_storage_path: str | None = None,
) -> dict:
    """Task 1: Download or validate trend video, upload to Supabase Storage."""
    logger.info("Starting download_trend", extra={"job_id": job_id, "trend_source": trend_source})

    try:
        # Update job status
        supabase.table("jobs").update({
            "status": "running",
        }).eq("id", job_id).execute()

        # Load job to get persona_id
        job = supabase.table("jobs").select("persona_id").eq("id", job_id).single().execute().data

        storage = StorageService()

        if trend_source == "url":
            # Download via yt-dlp
            downloader = Downloader()
            local_path = downloader.download_trend(trend_url, job_id)

            with open(local_path, "rb") as f:
                file_bytes = f.read()

            upload_result = storage.upload(
                file_bytes=file_bytes,
                persona_id=job["persona_id"],
                job_id=job_id,
                asset_type="trend",
                extension="mp4",
                mime_type="video/mp4",
            )
        elif trend_source == "upload":
            # File already in Storage, validate it exists
            if not trend_storage_path:
                raise ValueError("trend_storage_path is required when trend_source is 'upload'")

            public_url = storage.get_public_url(trend_storage_path)
            upload_result = {
                "storage_path": trend_storage_path,
                "public_url": public_url,
                "file_size": 0,
            }
        else:
            raise ValueError(f"Invalid trend_source: {trend_source}")

        # Create asset record
        asset_result = supabase.table("assets").insert({
            "job_id": job_id,
            "persona_id": job["persona_id"],
            "type": "trend",
            "storage_path": upload_result["storage_path"],
            "public_url": upload_result["public_url"],
            "file_size": upload_result["file_size"],
            "mime_type": "video/mp4",
        }).execute()

        asset_id = asset_result.data[0]["id"]

        # Update job
        supabase.table("jobs").update({
            "current_step": "trend_ready",
            "trend_asset_id": asset_id,
        }).eq("id", job_id).execute()

        logger.info("download_trend complete", extra={"job_id": job_id, "asset_id": asset_id})
        return {"job_id": job_id, "asset_id": asset_id}

    except Exception as exc:
        supabase.table("jobs").update({
            "status": "failed",
            "error_message": str(exc)[:1000],
        }).eq("id", job_id).execute()
        logger.error("download_trend failed", extra={"job_id": job_id, "error": str(exc)})
        raise self.retry(exc=exc)
