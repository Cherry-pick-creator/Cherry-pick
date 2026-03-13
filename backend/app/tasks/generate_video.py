import logging

from app.celery_app import celery
from app.database import supabase
from app.services.fal_client import FalClient
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    name="app.tasks.generate_video",
    max_retries=0,
    soft_time_limit=650,
    time_limit=660,
)
def generate_video(
    self,
    _prev_result: dict | None = None,
    job_id: str = "",
    persona_id: str = "",
    video_duration: int = 5,
) -> dict:
    """Task 3: Generate video via fal.ai Kling v2.6 Motion Control."""
    logger.info(
        "Starting generate_video",
        extra={"job_id": job_id, "persona_id": persona_id, "duration": video_duration},
    )

    try:
        # Update job step
        supabase.table("jobs").update({
            "current_step": "video_ready",
        }).eq("id", job_id).execute()

        # Load persona
        persona = supabase.table("personas").select("*").eq("id", persona_id).single().execute().data

        # Load asset URLs from job
        job = supabase.table("jobs").select(
            "image_asset_id, trend_asset_id"
        ).eq("id", job_id).single().execute().data

        # Get image public URL
        image_asset = supabase.table("assets").select(
            "public_url"
        ).eq("id", job["image_asset_id"]).single().execute().data

        # Get trend public URL
        trend_asset = supabase.table("assets").select(
            "public_url"
        ).eq("id", job["trend_asset_id"]).single().execute().data

        # Call fal.ai Kling
        fal = FalClient()
        result = fal.generate_video(
            prompt=persona["prompt_video"],
            image_url=image_asset["public_url"],
            video_url=trend_asset["public_url"],
            negative_prompt=persona.get("negative_prompt", ""),
            duration=video_duration,
        )

        # Download video from fal.ai (URLs expire)
        video_bytes = fal.download_file(result["url"])

        # Upload to Supabase Storage
        storage = StorageService()
        upload_result = storage.upload(
            file_bytes=video_bytes,
            persona_id=persona_id,
            job_id=job_id,
            asset_type="video_raw",
            extension="mp4",
            mime_type="video/mp4",
        )

        # Create asset record
        asset_result = supabase.table("assets").insert({
            "job_id": job_id,
            "persona_id": persona_id,
            "type": "video_raw",
            "storage_path": upload_result["storage_path"],
            "public_url": upload_result["public_url"],
            "file_size": upload_result["file_size"],
            "mime_type": "video/mp4",
            "metadata": {"seed": result.get("seed"), "duration": video_duration},
        }).execute()

        asset_id = asset_result.data[0]["id"]

        # Update job
        job_data = supabase.table("jobs").select("metadata").eq("id", job_id).single().execute().data
        job_metadata = job_data.get("metadata", {}) or {}
        job_metadata["video_duration"] = video_duration

        supabase.table("jobs").update({
            "current_step": "video_ready",
            "video_raw_asset_id": asset_id,
            "metadata": job_metadata,
        }).eq("id", job_id).execute()

        logger.info("generate_video complete", extra={"job_id": job_id, "asset_id": asset_id})
        return {"job_id": job_id, "asset_id": asset_id}

    except Exception as exc:
        supabase.table("jobs").update({
            "status": "failed",
            "error_message": str(exc)[:1000],
        }).eq("id", job_id).execute()
        logger.error("generate_video failed", extra={"job_id": job_id, "error": str(exc)})
        raise
