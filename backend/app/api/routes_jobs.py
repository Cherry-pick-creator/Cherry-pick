import logging

from fastapi import APIRouter, HTTPException, Query

from app.database import supabase
from app.schemas import (
    BatchDetailResponse,
    JobDetailResponse,
    JobListItem,
    JobListResponse,
    MessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    persona_id: str | None = Query(None),
    status: str | None = Query(None),
    type: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> JobListResponse:
    """List jobs with filters and pagination."""
    query = supabase.table("jobs").select("*", count="exact")

    if persona_id:
        query = query.eq("persona_id", persona_id)
    if status:
        query = query.eq("status", status)
    if type:
        query = query.eq("type", type)

    offset = (page - 1) * per_page
    query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)

    result = query.execute()

    # Get persona names
    persona_ids = list({j["persona_id"] for j in result.data})
    persona_names = {}
    if persona_ids:
        personas = supabase.table("personas").select("id, name").in_("id", persona_ids).execute()
        persona_names = {p["id"]: p["name"] for p in personas.data}

    items = [
        JobListItem(
            id=j["id"],
            persona_id=j["persona_id"],
            persona_name=persona_names.get(j["persona_id"], ""),
            type=j["type"],
            status=j["status"],
            current_step=j.get("current_step"),
            hook_text=j["hook_text"],
            created_at=j["created_at"],
            updated_at=j["updated_at"],
        )
        for j in result.data
    ]

    return JobListResponse(
        data=items,
        total=result.count or 0,
        page=page,
        per_page=per_page,
    )


@router.get("/batch/{batch_id}", response_model=BatchDetailResponse)
async def get_batch(batch_id: str) -> BatchDetailResponse:
    """Get batch detail with all child jobs."""
    batch_result = supabase.table("batch_jobs").select("*").eq(
        "id", batch_id
    ).single().execute()

    if not batch_result.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "BATCH_NOT_FOUND", "message": "Batch not found"},
        )

    batch = batch_result.data

    # Get all jobs in this batch
    jobs_result = supabase.table("jobs").select("*").eq(
        "batch_id", batch_id
    ).order("created_at").execute()

    # Get persona names
    persona_ids = list({j["persona_id"] for j in jobs_result.data})
    persona_names = {}
    if persona_ids:
        personas = supabase.table("personas").select("id, name").in_("id", persona_ids).execute()
        persona_names = {p["id"]: p["name"] for p in personas.data}

    jobs = [
        JobListItem(
            id=j["id"],
            persona_id=j["persona_id"],
            persona_name=persona_names.get(j["persona_id"], ""),
            type=j["type"],
            status=j["status"],
            current_step=j.get("current_step"),
            hook_text=j["hook_text"],
            created_at=j["created_at"],
            updated_at=j["updated_at"],
        )
        for j in jobs_result.data
    ]

    running = sum(1 for j in jobs if j.status in ("pending", "running"))

    return BatchDetailResponse(
        id=batch["id"],
        persona_id=batch["persona_id"],
        total=batch["total"],
        completed=batch["completed"],
        failed=batch["failed"],
        running=running,
        status=batch["status"],
        jobs=jobs,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str) -> JobDetailResponse:
    """Get full job detail with assets and timeline."""
    job_result = supabase.table("jobs").select("*").eq("id", job_id).single().execute()

    if not job_result.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "JOB_NOT_FOUND", "message": "Job not found"},
        )

    job = job_result.data

    # Get persona name
    persona_name = ""
    persona_result = supabase.table("personas").select("name").eq(
        "id", job["persona_id"]
    ).single().execute()
    if persona_result.data:
        persona_name = persona_result.data["name"]

    # Get assets
    assets_result = supabase.table("assets").select("*").eq(
        "job_id", job_id
    ).is_("deleted_at", "null").execute()

    assets_map = {}
    for asset in assets_result.data:
        assets_map[asset["type"]] = {
            "url": asset["public_url"],
            "type": asset["mime_type"],
        }

    # Build timeline from job metadata
    job_metadata = job.get("metadata", {}) or {}

    return JobDetailResponse(
        id=job["id"],
        persona_id=job["persona_id"],
        persona_name=persona_name,
        type=job["type"],
        status=job["status"],
        current_step=job.get("current_step"),
        hook_text=job["hook_text"],
        trend_url=job.get("trend_url"),
        assets=assets_map,
        timeline={"created": job["created_at"]},
        metadata=job_metadata,
        error_message=job.get("error_message"),
        celery_task_id=job.get("celery_task_id"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )


@router.delete("/{job_id}", response_model=MessageResponse)
async def cancel_job(job_id: str) -> MessageResponse:
    """Cancel a pending or running job."""
    job_result = supabase.table("jobs").select("id, status, celery_task_id").eq(
        "id", job_id
    ).single().execute()

    if not job_result.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "JOB_NOT_FOUND", "message": "Job not found"},
        )

    job = job_result.data

    if job["status"] not in ("pending", "running"):
        raise HTTPException(
            status_code=400,
            detail={"error": "JOB_NOT_CANCELLABLE", "message": "Cannot cancel a completed or failed job"},
        )

    # Revoke Celery task
    if job.get("celery_task_id"):
        from app.celery_app import celery
        celery.control.revoke(job["celery_task_id"], terminate=True)

    supabase.table("jobs").update({
        "status": "cancelled",
    }).eq("id", job_id).execute()

    logger.info("Job cancelled", extra={"job_id": job_id})
    return MessageResponse(message="Job cancelled")
