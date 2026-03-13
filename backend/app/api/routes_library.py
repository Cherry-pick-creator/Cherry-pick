import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.database import supabase
from app.schemas import LibraryListResponse, MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/", response_model=LibraryListResponse)
async def list_library(
    persona_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> LibraryListResponse:
    """List video_final assets (library view)."""
    query = supabase.table("assets").select(
        "*", count="exact"
    ).eq("type", "video_final").is_("deleted_at", "null")

    if persona_id:
        query = query.eq("persona_id", persona_id)

    offset = (page - 1) * per_page
    query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)

    result = query.execute()

    # Get persona names and hook_texts
    if result.data:
        persona_ids = list({a["persona_id"] for a in result.data})
        personas = supabase.table("personas").select("id, name").in_("id", persona_ids).execute()
        persona_names = {p["id"]: p["name"] for p in personas.data}

        job_ids = list({a["job_id"] for a in result.data})
        jobs = supabase.table("jobs").select("id, hook_text").in_("id", job_ids).execute()
        job_hooks = {j["id"]: j["hook_text"] for j in jobs.data}
    else:
        persona_names = {}
        job_hooks = {}

    items = [
        {
            "id": a["id"],
            "job_id": a["job_id"],
            "persona_id": a["persona_id"],
            "persona_name": persona_names.get(a["persona_id"], ""),
            "hook_text": job_hooks.get(a["job_id"], ""),
            "public_url": a["public_url"],
            "file_size": a.get("file_size"),
            "mime_type": a["mime_type"],
            "metadata": a.get("metadata", {}),
            "created_at": a["created_at"],
        }
        for a in result.data
    ]

    return LibraryListResponse(
        data=items,
        total=result.count or 0,
        page=page,
        per_page=per_page,
    )


@router.delete("/{asset_id}", response_model=MessageResponse)
async def delete_library_asset(asset_id: str) -> MessageResponse:
    """Soft delete a library asset."""
    existing = supabase.table("assets").select("id").eq(
        "id", asset_id
    ).eq("type", "video_final").is_("deleted_at", "null").execute()

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "ASSET_NOT_FOUND", "message": "Asset not found"},
        )

    supabase.table("assets").update({
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", asset_id).execute()

    logger.info("Library asset deleted", extra={"asset_id": asset_id})
    return MessageResponse(message="Asset deleted")
