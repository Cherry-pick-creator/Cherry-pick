import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.schemas import (
    MessageResponse,
    PersonaCreate,
    PersonaListResponse,
    PersonaResponse,
    PersonaUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/", response_model=PersonaListResponse)
async def list_personas() -> PersonaListResponse:
    """List all personas (excluding soft-deleted)."""
    result = supabase.table("personas").select("*").is_("deleted_at", "null").order(
        "updated_at", desc=True
    ).execute()

    items = []
    for p in result.data:
        # Count jobs for this persona
        job_count_result = supabase.table("jobs").select(
            "id", count="exact"
        ).eq("persona_id", p["id"]).execute()

        items.append({
            "id": p["id"],
            "name": p["name"],
            "description": p.get("description"),
            "palette": p.get("palette", {}),
            "font_family": p.get("font_family", ""),
            "created_at": p["created_at"],
            "updated_at": p["updated_at"],
            "job_count": job_count_result.count or 0,
        })

    return PersonaListResponse(data=items, total=len(items))


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: str) -> PersonaResponse:
    """Get a persona by ID with all fields."""
    result = supabase.table("personas").select("*").eq(
        "id", persona_id
    ).is_("deleted_at", "null").single().execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "PERSONA_NOT_FOUND", "message": "Persona not found"},
        )

    return PersonaResponse(**result.data)


@router.post("/", response_model=PersonaResponse, status_code=201)
async def create_persona(data: PersonaCreate) -> PersonaResponse:
    """Create a new persona."""
    # Check name uniqueness
    existing = supabase.table("personas").select("id").eq(
        "name", data.name
    ).is_("deleted_at", "null").execute()

    if existing.data:
        raise HTTPException(
            status_code=409,
            detail={"error": "PERSONA_NAME_CONFLICT", "message": "A persona with this name already exists"},
        )

    insert_data = data.model_dump()
    # Convert nested Pydantic models to dicts for JSONB
    insert_data["palette"] = data.palette.model_dump()
    insert_data["font_style"] = data.font_style.model_dump()

    result = supabase.table("personas").insert(insert_data).execute()

    logger.info("Persona created", extra={"persona_id": result.data[0]["id"], "name": data.name})
    return PersonaResponse(**result.data[0])


@router.patch("/{persona_id}", response_model=PersonaResponse)
async def update_persona(persona_id: str, data: PersonaUpdate) -> PersonaResponse:
    """Update a persona (partial update)."""
    # Check persona exists
    existing = supabase.table("personas").select("id").eq(
        "id", persona_id
    ).is_("deleted_at", "null").execute()

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "PERSONA_NOT_FOUND", "message": "Persona not found"},
        )

    # Check no running jobs
    _check_no_running_jobs(persona_id)

    # Check name uniqueness if name is being changed
    if data.name is not None:
        name_check = supabase.table("personas").select("id").eq(
            "name", data.name
        ).neq("id", persona_id).is_("deleted_at", "null").execute()

        if name_check.data:
            raise HTTPException(
                status_code=409,
                detail={"error": "PERSONA_NAME_CONFLICT", "message": "A persona with this name already exists"},
            )

    update_data = data.model_dump(exclude_unset=True)
    if "palette" in update_data and update_data["palette"] is not None:
        update_data["palette"] = data.palette.model_dump()
    if "font_style" in update_data and update_data["font_style"] is not None:
        update_data["font_style"] = data.font_style.model_dump()

    if not update_data:
        raise HTTPException(
            status_code=422,
            detail={"error": "PERSONA_VALIDATION_ERROR", "message": "No fields to update"},
        )

    result = supabase.table("personas").update(update_data).eq("id", persona_id).execute()

    logger.info("Persona updated", extra={"persona_id": persona_id})
    return PersonaResponse(**result.data[0])


@router.delete("/{persona_id}", response_model=MessageResponse)
async def delete_persona(persona_id: str) -> MessageResponse:
    """Soft delete a persona."""
    existing = supabase.table("personas").select("id").eq(
        "id", persona_id
    ).is_("deleted_at", "null").execute()

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail={"error": "PERSONA_NOT_FOUND", "message": "Persona not found"},
        )

    _check_no_running_jobs(persona_id)

    supabase.table("personas").update({
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", persona_id).execute()

    logger.info("Persona deleted", extra={"persona_id": persona_id})
    return MessageResponse(message="Persona deleted")


def _check_no_running_jobs(persona_id: str) -> None:
    """Raise 423 if persona has running or pending jobs."""
    running = supabase.table("jobs").select(
        "id", count="exact"
    ).eq("persona_id", persona_id).in_("status", ["pending", "running"]).execute()

    if running.count and running.count > 0:
        raise HTTPException(
            status_code=423,
            detail={"error": "PERSONA_LOCKED", "message": "Cannot modify persona while jobs are running"},
        )
