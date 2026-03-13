# API.md — Documentation API

> Chaque endpoint REST. Method, path, body, response, errors.

---

## Base URL

- **Dev :** `http://localhost:8000/api/v1`
- **Prod :** `https://cherrypick-engine.up.railway.app/api/v1`

Tous les endpoints sont préfixés `/api/v1`.

---

## Health

### GET /health

Vérifier que l'API, Redis et Supabase sont up.

**Response 200 :**
```json
{
  "status": "ok",
  "redis": "connected",
  "supabase": "connected",
  "version": "1.0.0"
}
```

---

## Personas

### GET /personas

Liste toutes les personas (hors soft-deleted).

**Query params :** aucun

**Response 200 :**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "CherryPick",
      "description": "AI influencer dev/indie hacker roast",
      "palette": { "primary": "#0A0A0A", "accent1": "#00E5FF", "accent2": "#8B5CF6", "text_color": "#F5F0EB", "bg_color": "#0A0A0A" },
      "font_family": "Bebas Neue",
      "created_at": "2026-03-01T00:00:00Z",
      "updated_at": "2026-03-01T00:00:00Z",
      "job_count": 42
    }
  ],
  "total": 1
}
```

### GET /personas/{id}

Détail d'une persona avec tous les champs (prompts inclus).

**Response 200 :** persona complète
**Response 404 :** `{ "error": "PERSONA_NOT_FOUND", "message": "Persona not found" }`

### POST /personas

Créer une persona.

**Body :**
```json
{
  "name": "CherryPick",
  "description": "AI influencer dev/indie hacker roast",
  "prompt_image_base": "A confident young woman wearing an elegant Venetian masquerade mask...",
  "prompt_image_variations": ["Variation 1 prompt...", "Variation 2 prompt..."],
  "prompt_video": "A confident seductive woman in a Venetian mask...",
  "negative_prompt": "cartoon, anime, illustration...",
  "palette": {
    "primary": "#0A0A0A",
    "accent1": "#00E5FF",
    "accent2": "#8B5CF6",
    "text_color": "#F5F0EB",
    "bg_color": "#0A0A0A"
  },
  "font_family": "Bebas Neue",
  "font_style": {
    "size": 72,
    "weight": "bold",
    "shadow": true,
    "position": "center"
  },
  "style_notes": "Sexy but not NSFW. Dark backgrounds with neon accents."
}
```

**Response 201 :** persona créée avec id
**Response 409 :** `{ "error": "PERSONA_NAME_CONFLICT", "message": "A persona with this name already exists" }`
**Response 422 :** validation errors

### PATCH /personas/{id}

Modifier une persona (champs partiels acceptés).

**Response 200 :** persona mise à jour
**Response 404 :** persona not found
**Response 409 :** nom déjà pris
**Response 423 :** `{ "error": "PERSONA_LOCKED", "message": "Cannot modify persona while jobs are running" }`

### DELETE /personas/{id}

Soft delete.

**Response 200 :** `{ "message": "Persona deleted" }`
**Response 404 :** persona not found
**Response 423 :** persona locked (jobs en cours)

---

## Generate

### POST /generate/single

Lancer la génération d'une vidéo.

**Body (multipart/form-data) :**
```
persona_id: uuid (required)
hook_text: string (required, 3-100 chars)
trend_source: "upload" | "url" (required)
trend_file: File (required si trend_source=upload, MP4, max 50Mo)
trend_url: string (required si trend_source=url)
image_variation: int (optionnel, index de la variation)
video_duration: int (optionnel, 5 ou 10, default 5)
font_override: JSON string (optionnel)
```

**Response 202 :**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Job created successfully"
}
```

**Response 404 :** persona not found
**Response 422 :** validation errors

### POST /generate/batch

Lancer la génération de N vidéos.

**Body (multipart/form-data) :**
```
persona_id: uuid (required)
items: JSON string (required) — array de { hook_text, trend_source, trend_url?, image_variation? }
trend_files: File[] (fichiers pour les items avec trend_source=upload)
```

**Response 202 :**
```json
{
  "batch_id": "uuid",
  "job_ids": ["uuid1", "uuid2", ...],
  "total": 7,
  "status": "pending"
}
```

---

## Jobs

### GET /jobs

Liste des jobs avec filtres et pagination.

**Query params :**
- persona_id (optionnel)
- status (optionnel) : pending | running | done | failed
- type (optionnel) : single | batch
- page (default 1)
- per_page (default 20, max 100)

**Response 200 :**
```json
{
  "data": [
    {
      "id": "uuid",
      "persona_id": "uuid",
      "persona_name": "CherryPick",
      "type": "single",
      "status": "done",
      "current_step": "complete",
      "hook_text": "Your SaaS solves a problem nobody has",
      "created_at": "2026-03-01T14:30:00Z",
      "updated_at": "2026-03-01T14:36:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

### GET /jobs/{id}

Détail complet d'un job.

**Response 200 :**
```json
{
  "id": "uuid",
  "persona_id": "uuid",
  "persona_name": "CherryPick",
  "type": "single",
  "status": "done",
  "current_step": "complete",
  "hook_text": "Your SaaS solves a problem nobody has",
  "trend_url": "https://tiktok.com/...",
  "assets": {
    "trend": { "url": "https://...", "type": "video/mp4" },
    "image": { "url": "https://...", "type": "image/png" },
    "video_raw": { "url": "https://...", "type": "video/mp4" },
    "video_final": { "url": "https://...", "type": "video/mp4" }
  },
  "timeline": {
    "created": "2026-03-01T14:30:00Z",
    "trend_ready": "2026-03-01T14:30:15Z",
    "image_ready": "2026-03-01T14:30:45Z",
    "video_ready": "2026-03-01T14:36:00Z",
    "complete": "2026-03-01T14:36:20Z"
  },
  "metadata": {
    "image_seed": 42,
    "video_duration": 5,
    "generation_cost_usd": 0.35,
    "total_time_seconds": 380
  },
  "error_message": null,
  "celery_task_id": "abc-123"
}
```

**Response 404 :** job not found

### GET /jobs/batch/{batch_id}

Détail d'un batch avec tous ses jobs.

**Response 200 :**
```json
{
  "id": "uuid",
  "persona_id": "uuid",
  "total": 7,
  "completed": 5,
  "failed": 1,
  "running": 1,
  "status": "running",
  "jobs": [ /* array de job objects */ ]
}
```

### DELETE /jobs/{id}

Annuler un job pending ou running. Revoke la task Celery.

**Response 200 :** `{ "message": "Job cancelled" }`
**Response 400 :** `{ "error": "JOB_NOT_CANCELLABLE", "message": "Cannot cancel a completed job" }`

---

## Library

### GET /library

Liste des assets de type video_final.

**Query params :**
- persona_id (optionnel)
- page (default 1)
- per_page (default 20)

**Response 200 :** array paginée d'assets avec URLs, metadata, persona info

### DELETE /library/{asset_id}

Soft delete un asset.

**Response 200 :** `{ "message": "Asset deleted" }`

---

*Dernière mise à jour : mars 2026*
