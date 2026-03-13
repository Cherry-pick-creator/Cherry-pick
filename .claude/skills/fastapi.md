# Skill: FastAPI

## Patterns obligatoires

### App setup (main.py)
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(title="CherryPick Engine", version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS.split(","), allow_methods=["*"], allow_headers=["*"])
app.include_router(personas_router, prefix="/api/v1")
app.include_router(generate_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
```

### Config (config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FAL_KEY: str
    REDIS_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SENTRY_DSN: str = ""
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: str = "http://localhost:3000"
    CELERY_CONCURRENCY: int = 3
    MAX_UPLOAD_SIZE_MB: int = 50
    TEMP_DIR: str = "/tmp/cherrypick"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Routes — pattern
- Un fichier par domaine (`routes_personas.py`, `routes_jobs.py`, etc.)
- `APIRouter` avec prefix et tags
- Pydantic models pour request ET response
- HTTPException pour les erreurs (pas de dict brut)
- Status codes explicites (201 pour create, 202 pour async)

### Error responses
```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail={"error": "PERSONA_NOT_FOUND", "message": "Persona not found"})
```

### File upload
```python
from fastapi import UploadFile, File, Form

@router.post("/generate/single", status_code=202)
async def generate_single(
    persona_id: str = Form(...),
    hook_text: str = Form(...),
    trend_source: str = Form(...),
    trend_file: UploadFile | None = File(None),
    trend_url: str | None = Form(None),
):
```

### Ne jamais faire dans les routes
- Appeler fal.ai directement
- Appeler yt-dlp directement
- Écrire sur le filesystem
- Avoir plus de 30 lignes de logique dans un endpoint
