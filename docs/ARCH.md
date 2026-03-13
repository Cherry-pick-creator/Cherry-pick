# ARCH.md — Architecture Technique

> Structure complète du projet. Chaque fichier, chaque module, chaque flux de données.

---

## 1. Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                     │
│              Next.js 14 + TypeScript + Tailwind          │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────────┐        │
│  │Dashboard │ │Personas  │ │Jobs  │ │Library │        │
│  │          │ │CRUD      │ │Track │ │Browse  │        │
│  └────┬─────┘ └────┬─────┘ └──┬───┘ └───┬────┘        │
│       │            │          │         │              │
│       └────────────┴────┬─────┴─────────┘              │
│                         │ REST API calls                │
└─────────────────────────┼──────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (Railway)                      │
│                      FastAPI                             │
│                                                         │
│  ┌──────────────┐    ┌──────────────────────┐          │
│  │  api/        │    │  services/            │          │
│  │  routes.py   │───▶│  fal_client.py       │          │
│  └──────┬───────┘    │  downloader.py       │          │
│         │            │  overlay.py          │          │
│         │ dispatch   │  storage.py          │          │
│         ▼            └──────────────────────┘          │
│  ┌──────────────┐              ▲                       │
│  │  tasks/      │              │ call                   │
│  │  generate.py │──────────────┘                       │
│  │  postprod.py │                                      │
│  │  pipeline.py │                                      │
│  └──────┬───────┘                                      │
│         │                                              │
└─────────┼──────────────────────────────────────────────┘
          │ broker
          ▼
┌──────────────────┐     ┌──────────────────────────────┐
│   Redis (broker)  │     │     Supabase                  │
│   Railway add-on  │     │  ┌────────────┐ ┌──────────┐│
└──────────────────┘     │  │ PostgreSQL │ │ Storage  ││
                         │  │ (tables)   │ │ (assets) ││
                         │  └────────────┘ └──────────┘│
                         └──────────────────────────────┘
                                    ▲
                                    │
                         ┌──────────┴──────────┐
                         │    fal.ai APIs       │
                         │  FLUX (images)       │
                         │  Kling (vidéos)      │
                         └─────────────────────┘
```

---

## 2. Structure des fichiers

```
cherrypick-engine/
├── CLAUDE.md
│
├── .claude/skills/
│   ├── fastapi.md
│   ├── celery-redis.md
│   ├── supabase.md
│   ├── nextjs.md
│   ├── fal-ai.md
│   └── ffmpeg-overlay.md
│
├── docs/
│   ├── CONTEXT.md
│   ├── SPEC.md
│   ├── ARCH.md              # ← ce fichier
│   ├── API.md
│   ├── INTEGRATIONS.md
│   ├── QUEUE.md
│   ├── ENV.md
│   ├── MIGRATIONS.md
│   ├── ERRORS.md
│   ├── SECURITY.md
│   ├── CONVENTIONS.md
│   ├── UI.md
│   ├── COPY.md
│   ├── TESTS.md
│   ├── DEPLOY.md
│   ├── MONITORING.md
│   ├── ANALYTICS.md
│   ├── BACKUP.md
│   ├── TASKS.md
│   ├── CHANGELOG.md
│   └── ROADMAP.md
│
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── Procfile
│   ├── railway.toml
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app, CORS, lifespan
│       ├── config.py            # Pydantic Settings (toutes les env vars)
│       ├── celery_app.py        # Celery instance + Redis broker config
│       ├── schemas.py           # Pydantic models (request/response)
│       ├── database.py          # Supabase client singleton
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes_personas.py    # CRUD personas
│       │   ├── routes_jobs.py        # Jobs management
│       │   ├── routes_generate.py    # Génération (single + batch)
│       │   ├── routes_library.py     # Bibliothèque assets
│       │   └── routes_health.py      # Health check
│       │
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── generate_image.py     # Task : FLUX image generation
│       │   ├── generate_video.py     # Task : Kling video generation
│       │   ├── download_trend.py     # Task : yt-dlp download
│       │   ├── postprod.py           # Task : text overlay + export
│       │   └── pipeline.py           # Task : orchestration chain complète
│       │
│       └── services/
│           ├── __init__.py
│           ├── fal_client.py         # Client fal.ai (FLUX + Kling)
│           ├── downloader.py         # yt-dlp wrapper
│           ├── overlay.py            # FFmpeg + Pillow text overlay
│           └── storage.py            # Supabase Storage (upload/download/list)
│
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   │
│   └── src/
│       ├── app/
│       │   ├── layout.tsx            # Root layout (sidebar + main content)
│       │   ├── page.tsx              # Dashboard (stats, jobs récents)
│       │   ├── personas/
│       │   │   ├── page.tsx          # Liste des personas
│       │   │   ├── new/
│       │   │   │   └── page.tsx      # Créer une persona
│       │   │   └── [id]/
│       │   │       └── page.tsx      # Éditer une persona
│       │   ├── generate/
│       │   │   └── page.tsx          # Formulaire génération (single + batch)
│       │   ├── jobs/
│       │   │   ├── page.tsx          # Liste des jobs
│       │   │   └── [id]/
│       │   │       └── page.tsx      # Détail d'un job (statut temps réel)
│       │   └── library/
│       │       └── page.tsx          # Bibliothèque vidéos (filtre par persona)
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx
│       │   │   └── Header.tsx
│       │   ├── personas/
│       │   │   ├── PersonaCard.tsx
│       │   │   └── PersonaForm.tsx
│       │   ├── jobs/
│       │   │   ├── JobCard.tsx
│       │   │   └── JobStatusBadge.tsx
│       │   ├── generate/
│       │   │   ├── GenerateForm.tsx
│       │   │   └── BatchPanel.tsx
│       │   ├── library/
│       │   │   └── VideoPreview.tsx
│       │   └── shared/
│       │       ├── LoadingSpinner.tsx
│       │       └── EmptyState.tsx
│       │
│       └── lib/
│           ├── api.ts                # Client API (fetch wrapper)
│           ├── types.ts              # Types TypeScript (mirrors schemas.py)
│           └── constants.ts          # Constantes UI
│
├── assets/
│   └── fonts/
│       └── .gitkeep
│
└── .gitignore
```

---

## 3. Flux de données — Pipeline complet

```
UTILISATEUR                   BACKEND                          SERVICES EXTERNES
─────────────────────────────────────────────────────────────────────────────

1. Upload trend video    ──▶  POST /generate/single
   + select persona           │
   + write hook text          ▼
                         Valider inputs (Pydantic)
                         Créer job en DB (status: pending)
                         Dispatch celery chain
                              │
                              ▼
                         ┌─ TASK 1: download_trend ──────▶ yt-dlp (si URL)
                         │  Ou : accepter fichier uploadé    │
                         │  Stocker dans Supabase Storage ◀──┘
                         │  Update job: step=trend_ready
                         │
                         ├─ TASK 2: generate_image ──────▶ fal.ai FLUX
                         │  Charger persona.prompt_image       │
                         │  Injecter variables (variation)     │
                         │  Stocker résultat Supabase ◀────────┘
                         │  Update job: step=image_ready
                         │
                         ├─ TASK 3: generate_video ──────▶ fal.ai Kling
                         │  Charger persona.prompt_video       │
                         │  Input: image + trend video         │
                         │  Poll status (3-6 min) ◀────────────┘
                         │  Stocker résultat Supabase
                         │  Update job: step=video_ready
                         │
                         ├─ TASK 4: postprod ─────────────▶ FFmpeg + Pillow
                         │  Charger persona.font + palette     │
                         │  Appliquer text overlay              │
                         │  Exporter MP4 sans watermark ◀──────┘
                         │  Stocker résultat Supabase
                         │  Update job: step=complete, status=done
                         │
                         └─ Retour au frontend via polling GET /jobs/{id}

2. Frontend poll         ──▶  GET /jobs/{id}
   toutes les 3s              Retourne: status, step, progress, URLs assets
```

---

## 4. Modèle de données (résumé)

Voir `docs/MIGRATIONS.md` pour le schéma complet.

```
personas
├── id (uuid, PK)
├── name (text, unique)
├── description (text)
├── prompt_image_base (text)         # Prompt FLUX de base
├── prompt_image_variations (jsonb)  # Array de prompts variants
├── prompt_video (text)              # Prompt Kling
├── negative_prompt (text)
├── palette (jsonb)                  # {primary, accent1, accent2, text, bg}
├── font_family (text)              # Ex: "Bebas Neue"
├── font_style (jsonb)              # {size, weight, shadow, position}
├── style_notes (text)              # Notes libres sur le style
├── created_at (timestamptz)
└── updated_at (timestamptz)

jobs
├── id (uuid, PK)
├── persona_id (uuid, FK → personas)
├── type (text)                     # single | batch
├── status (text)                   # pending | running | done | failed
├── current_step (text)             # trend_ready | image_ready | video_ready | complete
├── hook_text (text)                # Le text overlay
├── trend_url (text, nullable)      # URL TikTok si download
├── trend_asset_id (uuid, FK → assets, nullable)
├── image_asset_id (uuid, FK → assets, nullable)
├── video_raw_asset_id (uuid, FK → assets, nullable)
├── video_final_asset_id (uuid, FK → assets, nullable)
├── celery_task_id (text)
├── error_message (text, nullable)
├── metadata (jsonb)                # Durée génération, coûts, params
├── created_at (timestamptz)
└── updated_at (timestamptz)

assets
├── id (uuid, PK)
├── job_id (uuid, FK → jobs)
├── persona_id (uuid, FK → personas)
├── type (text)                     # trend | image | video_raw | video_final
├── storage_path (text)             # Path dans Supabase Storage
├── public_url (text)
├── file_size (bigint)
├── mime_type (text)
├── metadata (jsonb)                # Dimensions, durée, seed, etc.
├── created_at (timestamptz)
└── deleted_at (timestamptz, nullable)

batch_jobs
├── id (uuid, PK)
├── persona_id (uuid, FK → personas)
├── job_ids (uuid[], array de FK → jobs)
├── total (int)
├── completed (int)
├── failed (int)
├── status (text)                   # pending | running | done | partial
├── created_at (timestamptz)
└── updated_at (timestamptz)
```

---

## 5. Séparation des responsabilités

### api/ — Routes HTTP (zéro logique métier)

Les routes valident les inputs (Pydantic), appellent les tasks ou la DB, et retournent des réponses JSON. Elles ne font JAMAIS d'appel à fal.ai, FFmpeg, ou yt-dlp directement.

### tasks/ — Celery tasks (orchestration)

Les tasks sont le lien entre l'API et les services. Elles gèrent les retries, les timeouts, les mises à jour de statut en DB, et la chaîne d'exécution. Elles appellent les services pour le travail réel.

### services/ — Logique métier pure (stateless)

Les services font le travail : appeler fal.ai, télécharger une vidéo, appliquer un overlay, uploader dans Supabase. Ils sont stateless, testables unitairement, et ne connaissent pas Celery.

**Règle : routes → tasks → services. Jamais de raccourci.**

---

## 6. Communication frontend ↔ backend

- **REST API** uniquement (pas de WebSocket en V1)
- **Polling** pour le suivi des jobs : le frontend poll `GET /jobs/{id}` toutes les 3 secondes tant que `status !== done|failed`
- **CORS** configuré pour le domaine Vercel uniquement
- **Pas d'auth en V1** (outil interne). Préparé dans l'architecture pour V2.

---

## 7. Storage strategy

- **Supabase Storage** pour tous les fichiers (trends, images, vidéos raw, vidéos finales)
- **Bucket `assets`** avec structure : `{persona_id}/{job_id}/{type}_{timestamp}.{ext}`
- **Railway filesystem est éphémère** — jamais stocker de fichiers sur Railway. Tout passe par Supabase Storage.
- **Fichiers temporaires** pendant le processing : `/tmp/cherrypick/{job_id}/` — nettoyé après upload vers Supabase.

---

*Dernière mise à jour : mars 2026*
