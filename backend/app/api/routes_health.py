import logging

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API, Redis, and Supabase connectivity."""
    redis_status = "disconnected"
    supabase_status = "disconnected"

    # Check Redis
    try:
        import redis as redis_lib

        r = redis_lib.from_url(settings.REDIS_URL, socket_timeout=3)
        r.ping()
        redis_status = "connected"
    except Exception as exc:
        logger.warning("Redis health check failed", extra={"error": str(exc)})

    # Check Supabase
    try:
        from app.database import supabase

        supabase.table("personas").select("id").limit(1).execute()
        supabase_status = "connected"
    except Exception as exc:
        logger.warning("Supabase health check failed", extra={"error": str(exc)})

    status = "ok" if redis_status == "connected" and supabase_status == "connected" else "degraded"

    return HealthResponse(
        status=status,
        redis=redis_status,
        supabase=supabase_status,
        version=settings.APP_VERSION,
    )
