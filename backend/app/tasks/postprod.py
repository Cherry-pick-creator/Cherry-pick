import logging
import os

from app.celery_app import celery
from app.config import settings
from app.database import supabase
from app.services.overlay import OverlayService
from app.services.storage import StorageService, cleanup_temp_dir

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    name="app.tasks.postprod",
    max_retries=1,
    default_retry_delay=5,
    soft_time_limit=115,
    time_limit=120,
)
def postprod(
    self,
    _prev_result: dict | None = None,
    job_id: str = "",
    persona_id: str = "",
    hook_text: str = "",
    font_override: dict | None = None,
) -> dict:
    """Task 4: Apply text overlay + export final MP4."""
    logger.info(
        "Starting postprod",
        extra={"job_id": job_id, "persona_id": persona_id, "hook_text": hook_text},
    )

    try:
        # Load persona
        persona = supabase.table("personas").select("*").eq("id", persona_id).single().execute().data

        # Load video_raw asset
        job = supabase.table("jobs").select(
            "video_raw_asset_id"
        ).eq("id", job_id).single().execute().data

        video_raw_asset = supabase.table("assets").select(
            "storage_path"
        ).eq("id", job["video_raw_asset_id"]).single().execute().data

        # Download video_raw to temp
        job_dir = os.path.join(settings.TEMP_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        video_raw_path = os.path.join(job_dir, "video_raw.mp4")

        storage = StorageService()
        storage.download_to_file(video_raw_asset["storage_path"], video_raw_path)

        # Prepare font_style (with optional override)
        font_style = persona.get("font_style", {})
        if font_override:
            font_style = {**font_style, **font_override}

        palette = persona.get("palette", {})
        font_family = persona.get("font_family", "Bebas Neue")

        # Apply overlay
        overlay_service = OverlayService()
        output_path = os.path.join(job_dir, "video_final.mp4")

        overlay_service.process(
            video_path=video_raw_path,
            text=hook_text,
            font_family=font_family,
            font_style=font_style,
            palette=palette,
            output_path=output_path,
        )

        # Upload final video to Supabase Storage
        with open(output_path, "rb") as f:
            final_bytes = f.read()

        upload_result = storage.upload(
            file_bytes=final_bytes,
            persona_id=persona_id,
            job_id=job_id,
            asset_type="video_final",
            extension="mp4",
            mime_type="video/mp4",
        )

        # Create asset record
        asset_result = supabase.table("assets").insert({
            "job_id": job_id,
            "persona_id": persona_id,
            "type": "video_final",
            "storage_path": upload_result["storage_path"],
            "public_url": upload_result["public_url"],
            "file_size": upload_result["file_size"],
            "mime_type": "video/mp4",
        }).execute()

        asset_id = asset_result.data[0]["id"]

        # Update job: complete
        job_data = supabase.table("jobs").select("metadata, created_at").eq("id", job_id).single().execute().data
        job_metadata = job_data.get("metadata", {}) or {}
        # Estimate cost: ~$0.05 image + ~$0.20 video
        job_metadata["generation_cost_usd"] = round(0.05 + 0.20, 2)

        supabase.table("jobs").update({
            "status": "done",
            "current_step": "complete",
            "video_final_asset_id": asset_id,
            "metadata": job_metadata,
        }).eq("id", job_id).execute()

        logger.info("postprod complete", extra={"job_id": job_id, "asset_id": asset_id})

        # Update batch_job if applicable
        _update_batch_status(job_id)

        return {"job_id": job_id, "asset_id": asset_id}

    except Exception as exc:
        supabase.table("jobs").update({
            "status": "failed",
            "error_message": str(exc)[:1000],
        }).eq("id", job_id).execute()
        logger.error("postprod failed", extra={"job_id": job_id, "error": str(exc)})
        _update_batch_status(job_id)
        raise self.retry(exc=exc)

    finally:
        cleanup_temp_dir(job_id)


def _update_batch_status(job_id: str) -> None:
    """Update parent batch_job counters if this job belongs to a batch."""
    try:
        job = supabase.table("jobs").select("batch_id, status").eq("id", job_id).single().execute().data
        batch_id = job.get("batch_id")
        if not batch_id:
            return

        # Count statuses of all jobs in this batch
        batch_jobs = supabase.table("jobs").select("status").eq("batch_id", batch_id).execute().data
        completed = sum(1 for j in batch_jobs if j["status"] == "done")
        failed = sum(1 for j in batch_jobs if j["status"] == "failed")
        total = len(batch_jobs)

        if completed + failed == total:
            if failed == total:
                batch_status = "failed"
            elif failed > 0:
                batch_status = "partial"
            else:
                batch_status = "done"
        else:
            batch_status = "running"

        supabase.table("batch_jobs").update({
            "completed": completed,
            "failed": failed,
            "status": batch_status,
        }).eq("id", batch_id).execute()

    except Exception as exc:
        logger.error("Failed to update batch status", extra={"job_id": job_id, "error": str(exc)})
