import json
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.database import supabase
from app.schemas import GenerateBatchResponse, GenerateSingleResponse
from app.services.downloader import Downloader
from app.services.storage import StorageService
from app.tasks.pipeline import run_pipeline_batch, run_pipeline_single

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/single", response_model=GenerateSingleResponse, status_code=202)
async def generate_single(
    persona_id: str = Form(...),
    hook_text: str = Form(...),
    trend_source: str = Form(...),
    trend_file: UploadFile | None = File(None),
    trend_url: str | None = Form(None),
    image_variation: int | None = Form(None),
    video_duration: int = Form(5),
    font_override: str | None = Form(None),
) -> GenerateSingleResponse:
    """Launch single video generation pipeline."""
    # Validate inputs
    _validate_hook_text(hook_text)
    _validate_trend_source(trend_source, trend_file, trend_url)
    _validate_persona_exists(persona_id)
    _validate_video_duration(video_duration)

    parsed_font_override = None
    if font_override:
        try:
            parsed_font_override = json.loads(font_override)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=422,
                detail={"error": "PERSONA_VALIDATION_ERROR", "message": "font_override must be valid JSON"},
            )

    # Handle trend file upload if needed
    trend_storage_path = None
    if trend_source == "upload" and trend_file:
        file_bytes = await trend_file.read()
        Downloader.validate_upload(file_bytes, trend_file.content_type)

        # Create a placeholder job_id to organize storage
        job_insert = supabase.table("jobs").insert({
            "persona_id": persona_id,
            "type": "single",
            "status": "pending",
            "hook_text": hook_text,
            "trend_url": trend_url,
            "image_variation": image_variation,
            "video_duration": video_duration,
            "font_override": parsed_font_override,
        }).execute()
        job_id = job_insert.data[0]["id"]

        # Upload trend to storage
        storage = StorageService()
        upload_result = storage.upload(
            file_bytes=file_bytes,
            persona_id=persona_id,
            job_id=job_id,
            asset_type="trend",
            extension="mp4",
            mime_type="video/mp4",
        )
        trend_storage_path = upload_result["storage_path"]
    else:
        # Create job
        job_insert = supabase.table("jobs").insert({
            "persona_id": persona_id,
            "type": "single",
            "status": "pending",
            "hook_text": hook_text,
            "trend_url": trend_url,
            "image_variation": image_variation,
            "video_duration": video_duration,
            "font_override": parsed_font_override,
        }).execute()
        job_id = job_insert.data[0]["id"]

    # Launch pipeline
    celery_task_id = run_pipeline_single(
        job_id=job_id,
        persona_id=persona_id,
        trend_source=trend_source,
        trend_url=trend_url,
        trend_storage_path=trend_storage_path,
        image_variation=image_variation,
        video_duration=video_duration,
        hook_text=hook_text,
        font_override=parsed_font_override,
    )

    # Save celery task ID
    supabase.table("jobs").update({
        "celery_task_id": celery_task_id,
    }).eq("id", job_id).execute()

    logger.info("Single generation launched", extra={"job_id": job_id, "celery_task_id": celery_task_id})
    return GenerateSingleResponse(job_id=job_id)


@router.post("/batch", response_model=GenerateBatchResponse, status_code=202)
async def generate_batch(
    persona_id: str = Form(...),
    items: str = Form(...),
    trend_files: list[UploadFile] = File(default=[]),
) -> GenerateBatchResponse:
    """Launch batch video generation (N pipelines in parallel)."""
    _validate_persona_exists(persona_id)

    # Parse items JSON
    try:
        items_list = json.loads(items)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail={"error": "PERSONA_VALIDATION_ERROR", "message": "items must be valid JSON array"},
        )

    if not isinstance(items_list, list):
        raise HTTPException(
            status_code=422,
            detail={"error": "PERSONA_VALIDATION_ERROR", "message": "items must be an array"},
        )

    if len(items_list) < 2:
        raise HTTPException(
            status_code=422,
            detail={"error": "BATCH_TOO_SMALL", "message": "Batch must contain at least 2 items"},
        )

    if len(items_list) > 10:
        raise HTTPException(
            status_code=422,
            detail={"error": "BATCH_TOO_LARGE", "message": "Batch must contain at most 10 items"},
        )

    # Validate each item
    for item in items_list:
        _validate_hook_text(item.get("hook_text", ""))
        _validate_trend_source(
            item.get("trend_source", ""),
            None,
            item.get("trend_url"),
        )

    # Create batch_job
    batch_insert = supabase.table("batch_jobs").insert({
        "persona_id": persona_id,
        "total": len(items_list),
        "status": "pending",
    }).execute()
    batch_id = batch_insert.data[0]["id"]

    # Create individual jobs + prepare pipeline configs
    job_ids: list[str] = []
    jobs_config: list[dict] = []
    file_index = 0

    storage = StorageService()

    for item in items_list:
        job_insert = supabase.table("jobs").insert({
            "persona_id": persona_id,
            "batch_id": batch_id,
            "type": "batch",
            "status": "pending",
            "hook_text": item["hook_text"],
            "trend_url": item.get("trend_url"),
            "image_variation": item.get("image_variation"),
            "video_duration": item.get("video_duration", 5),
        }).execute()
        job_id = job_insert.data[0]["id"]
        job_ids.append(job_id)

        trend_storage_path = None
        if item.get("trend_source") == "upload" and file_index < len(trend_files):
            file_bytes = await trend_files[file_index].read()
            Downloader.validate_upload(file_bytes, trend_files[file_index].content_type)
            upload_result = storage.upload(
                file_bytes=file_bytes,
                persona_id=persona_id,
                job_id=job_id,
                asset_type="trend",
                extension="mp4",
                mime_type="video/mp4",
            )
            trend_storage_path = upload_result["storage_path"]
            file_index += 1

        jobs_config.append({
            "job_id": job_id,
            "trend_source": item["trend_source"],
            "trend_url": item.get("trend_url"),
            "trend_storage_path": trend_storage_path,
            "image_variation": item.get("image_variation"),
            "video_duration": item.get("video_duration", 5),
            "hook_text": item["hook_text"],
            "font_override": item.get("font_override"),
        })

    # Launch batch pipeline
    run_pipeline_batch(
        batch_id=batch_id,
        persona_id=persona_id,
        jobs_config=jobs_config,
    )

    # Update batch status
    supabase.table("batch_jobs").update({"status": "running"}).eq("id", batch_id).execute()

    logger.info("Batch generation launched", extra={"batch_id": batch_id, "count": len(job_ids)})
    return GenerateBatchResponse(batch_id=batch_id, job_ids=job_ids, total=len(job_ids))


# ── Validators ──────────────────────────────

def _validate_hook_text(hook_text: str) -> None:
    if len(hook_text) < 3:
        raise HTTPException(
            status_code=422,
            detail={"error": "HOOK_TEXT_TOO_SHORT", "message": "hook_text must be at least 3 characters"},
        )
    if len(hook_text) > 100:
        raise HTTPException(
            status_code=422,
            detail={"error": "HOOK_TEXT_TOO_LONG", "message": "hook_text must be at most 100 characters"},
        )


def _validate_trend_source(
    trend_source: str,
    trend_file: UploadFile | None,
    trend_url: str | None,
) -> None:
    if trend_source not in ("upload", "url"):
        raise HTTPException(
            status_code=422,
            detail={"error": "INVALID_TREND_SOURCE", "message": 'trend_source must be "upload" or "url"'},
        )
    if trend_source == "upload" and trend_file is None and trend_url is None:
        pass  # File might be provided separately in batch
    if trend_source == "url" and not trend_url:
        raise HTTPException(
            status_code=422,
            detail={"error": "MISSING_TREND_URL", "message": 'trend_url is required when trend_source is "url"'},
        )


def _validate_persona_exists(persona_id: str) -> None:
    result = supabase.table("personas").select("id").eq(
        "id", persona_id
    ).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "INVALID_PERSONA", "message": "Persona not found"},
        )


def _validate_video_duration(duration: int) -> None:
    if duration not in (5, 10):
        raise HTTPException(
            status_code=422,
            detail={"error": "PERSONA_VALIDATION_ERROR", "message": "video_duration must be 5 or 10"},
        )
