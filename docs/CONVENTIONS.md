# CONVENTIONS.md — Standards de Code

---

## Python (backend/)

### Naming
- **Fichiers :** snake_case (`fal_client.py`, `generate_image.py`)
- **Classes :** PascalCase (`PersonaCreate`, `JobResponse`)
- **Fonctions :** snake_case (`generate_image`, `download_trend`)
- **Constantes :** UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Variables :** snake_case (`job_id`, `persona_name`)

### Structure d'un service
```python
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class FalClient:
    """Client pour les appels fal.ai."""
    
    def __init__(self):
        self.api_key = settings.FAL_KEY
    
    async def generate_image(self, prompt: str, seed: int | None = None) -> dict:
        """Génère une image via FLUX. Returns dict avec url et seed."""
        logger.info("Generating image", extra={"prompt_length": len(prompt), "seed": seed})
        # ... implementation
```

### Structure d'une task Celery
```python
import logging
from app.celery_app import celery
from app.services.fal_client import FalClient

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=1, default_retry_delay=15)
def generate_image(self, job_id: str, persona_id: str, image_variation: int | None = None):
    """Task Celery : génération d'image FLUX."""
    logger.info("Starting image generation", extra={"job_id": job_id, "persona_id": persona_id})
    try:
        # 1. Charger persona
        # 2. Appeler service
        # 3. Update job en DB
    except Exception as exc:
        # Update job status = failed
        logger.error("Image generation failed", extra={"job_id": job_id, "error": str(exc)})
        raise self.retry(exc=exc)
```

### Structure d'une route
```python
from fastapi import APIRouter, HTTPException
from app.schemas import PersonaCreate, PersonaResponse
from app.database import supabase

router = APIRouter(prefix="/personas", tags=["personas"])

@router.post("/", response_model=PersonaResponse, status_code=201)
async def create_persona(data: PersonaCreate):
    """Créer une nouvelle persona."""
    # Validation faite par Pydantic
    # Logique minimale, pas d'appel service externe
    result = supabase.table("personas").insert(data.model_dump()).execute()
    return result.data[0]
```

### Logging
- Toujours JSON structuré
- Inclure `job_id`, `persona_id` quand disponible
- Niveaux : DEBUG (dev only), INFO (opérations normales), WARNING (dégradé), ERROR (échecs)
- JAMAIS de `print()`

### Type hints
- Obligatoires sur toutes les fonctions (params + return)
- Utiliser `X | None` (pas `Optional[X]`)
- Utiliser Pydantic pour la validation des inputs API

### Imports (ordre isort)
```python
# 1. Standard library
import logging
import os
from datetime import datetime

# 2. Third-party
from celery import chain
from fastapi import APIRouter
from pydantic import BaseModel

# 3. Local
from app.config import settings
from app.services.fal_client import FalClient
```

---

## TypeScript (frontend/)

### Naming
- **Fichiers composants :** PascalCase (`JobCard.tsx`, `PersonaForm.tsx`)
- **Fichiers utilitaires :** camelCase (`api.ts`, `types.ts`)
- **Interfaces/Types :** PascalCase préfixé par rien (`Persona`, `Job`, pas `IPersona`)
- **Fonctions :** camelCase (`fetchJobs`, `createPersona`)
- **Constantes :** UPPER_SNAKE_CASE (`API_BASE_URL`)

### Composants React
```tsx
"use client";
import { useState } from "react";

interface Props {
  personaId: string;
  onSubmit: (data: GenerateInput) => void;
}

export default function GenerateForm({ personaId, onSubmit }: Props) {
  const [hookText, setHookText] = useState("");
  // ...
}
```

### Pas de `any`. Jamais. Utiliser `unknown` puis narrower.

### Client API
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json();
    throw new ApiError(error.error, error.message, res.status);
  }
  return res.json();
}
```

---

## Git

### Commits
Format : `type: description courte`
- `feat: add persona CRUD endpoints`
- `fix: handle fal.ai timeout in generate_video`
- `refactor: extract overlay logic to service`
- `docs: update API.md with batch endpoint`
- `chore: update dependencies`

### Branches
- `main` — production
- `feat/xxx` — nouvelles features
- `fix/xxx` — corrections

---

*Dernière mise à jour : mars 2026*
