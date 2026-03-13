import json
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields (job_id, persona_id, etc.)
        if hasattr(record, "job_id"):
            log_entry["job_id"] = record.job_id
        if hasattr(record, "persona_id"):
            log_entry["persona_id"] = record.persona_id
        # Include any extra dict passed via extra={}
        for key in ("error", "elapsed_s", "file_size", "storage_path",
                     "seed", "request_id", "prompt_length", "status",
                     "env", "version", "duration"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry)


# Configure structured logging
handler = logging.StreamHandler(sys.stdout)
if settings.APP_ENV == "production":
    handler.setFormatter(JsonFormatter())
else:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[handler],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CherryPick Engine starting", extra={"env": settings.APP_ENV, "version": settings.APP_VERSION})

    # Init Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.1,
            environment=settings.APP_ENV,
        )

    yield

    logger.info("CherryPick Engine shutting down")


app = FastAPI(
    title="CherryPick Engine",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.api.routes_health import router as health_router
from app.api.routes_personas import router as personas_router
from app.api.routes_generate import router as generate_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_library import router as library_router

app.include_router(health_router, prefix="/api/v1")
app.include_router(personas_router, prefix="/api/v1")
app.include_router(generate_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
