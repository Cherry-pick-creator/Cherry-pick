import logging

from app.celery_app import celery
from app.database import supabase
from app.services.fal_client import FalClient
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    name="app.tasks.generate_image",
    max_retries=1,
    default_retry_delay=15,
    soft_time_limit=85,
    time_limit=90,
)
def generate_image(
    self,
    _prev_result: dict | None = None,
    job_id: str = "",
    persona_id: str = "",
    image_variation: int | None = None,
) -> dict:
    """Task 2: Generate image via fal.ai FLUX 1.1 Pro."""
    logger.info(
        "Starting generate_image",
        extra={"job_id": job_id, "persona_id": persona_id, "variation": image_variation},
    )

    try:
        # Update job status
        supabase.table("jobs").update({
            "current_step": "image_ready",
        }).eq("id", job_id).execute()

        # Load persona
        persona = supabase.table("personas").select("*").eq("id", persona_id).single().execute().data

        # Select prompt
        if image_variation is not None:
            variations = persona.get("prompt_image_variations", [])
            if 0 <= image_variation < len(variations):
                prompt = variations[image_variation]
            else:
                logger.warning(
                    "Variation index out of range, using base prompt",
                    extra={"job_id": job_id, "variation": image_variation, "max": len(variations)},
                )
                prompt = persona["prompt_image_base"]
        else:
            prompt = persona["prompt_image_base"]

        negative_prompt = persona.get("negative_prompt", "")

        # Call fal.ai FLUX
        fal = FalClient()
        result = fal.generate_image(prompt=prompt, negative_prompt=negative_prompt)

        # Download image from fal.ai (URLs expire)
        image_bytes = fal.download_file(result["url"])

        # Upload to Supabase Storage
        storage = StorageService()
        upload_result = storage.upload(
            file_bytes=image_bytes,
            persona_id=persona_id,
            job_id=job_id,
            asset_type="image",
            extension="png",
            mime_type="image/png",
        )

        # Create asset record
        asset_result = supabase.table("assets").insert({
            "job_id": job_id,
            "persona_id": persona_id,
            "type": "image",
            "storage_path": upload_result["storage_path"],
            "public_url": upload_result["public_url"],
            "file_size": upload_result["file_size"],
            "mime_type": "image/png",
            "metadata": {"seed": result.get("seed")},
        }).execute()

        asset_id = asset_result.data[0]["id"]

        # Update job
        update_data: dict = {
            "current_step": "image_ready",
            "image_asset_id": asset_id,
        }
        # Store seed in job metadata
        job = supabase.table("jobs").select("metadata").eq("id", job_id).single().execute().data
        job_metadata = job.get("metadata", {}) or {}
        job_metadata["image_seed"] = result.get("seed")
        update_data["metadata"] = job_metadata

        supabase.table("jobs").update(update_data).eq("id", job_id).execute()

        logger.info("generate_image complete", extra={"job_id": job_id, "asset_id": asset_id})
        return {"job_id": job_id, "asset_id": asset_id}

    except Exception as exc:
        supabase.table("jobs").update({
            "status": "failed",
            "error_message": str(exc)[:1000],
        }).eq("id", job_id).execute()
        logger.error("generate_image failed", extra={"job_id": job_id, "error": str(exc)})
        raise self.retry(exc=exc)
