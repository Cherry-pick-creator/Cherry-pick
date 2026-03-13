# ENV.md — Variables d'Environnement

> Chaque variable : nom, description, required/optional, valeur par défaut, quel service l'utilise.

---

## Backend

| Variable | Description | Required | Default | Service |
|----------|-------------|----------|---------|---------|
| `FAL_KEY` | API key fal.ai (FLUX + Kling) | ✅ | — | fal_client.py |
| `REDIS_URL` | URL de connexion Redis (broker Celery) | ✅ | — | celery_app.py |
| `SUPABASE_URL` | URL du projet Supabase | ✅ | — | database.py, storage.py |
| `SUPABASE_SERVICE_KEY` | Service role key Supabase (full access) | ✅ | — | database.py, storage.py |
| `SUPABASE_ANON_KEY` | Anon key Supabase (pour le frontend uniquement) | ❌ | — | — |
| `SENTRY_DSN` | DSN Sentry pour error tracking | ❌ | — | main.py |
| `APP_ENV` | Environnement (development / staging / production) | ❌ | development | config.py |
| `APP_VERSION` | Version de l'app (affiché dans /health) | ❌ | 1.0.0 | config.py |
| `CORS_ORIGINS` | Origins autorisés (comma-separated) | ❌ | http://localhost:3000 | main.py |
| `CELERY_CONCURRENCY` | Nombre de workers Celery | ❌ | 3 | celery_app.py |
| `MAX_UPLOAD_SIZE_MB` | Taille max upload trend en Mo | ❌ | 50 | routes_generate.py |
| `TEMP_DIR` | Répertoire temporaire pour le processing | ❌ | /tmp/cherrypick | overlay.py, downloader.py |
| `LOG_LEVEL` | Niveau de log (DEBUG/INFO/WARNING/ERROR) | ❌ | INFO | main.py |

## Frontend

| Variable | Description | Required | Default | Usage |
|----------|-------------|----------|---------|-------|
| `NEXT_PUBLIC_API_URL` | URL de l'API backend | ✅ | — | lib/api.ts |
| `NEXT_PUBLIC_APP_NAME` | Nom affiché dans l'UI | ❌ | CherryPick Engine | layout.tsx |

## .env.example (backend)

```env
# === REQUIRED ===
FAL_KEY=
REDIS_URL=redis://localhost:6379/0
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=

# === OPTIONAL ===
SENTRY_DSN=
APP_ENV=development
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000
CELERY_CONCURRENCY=3
MAX_UPLOAD_SIZE_MB=50
TEMP_DIR=/tmp/cherrypick
LOG_LEVEL=INFO
```

## .env.example (frontend)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=CherryPick Engine
```

---

## Notes Railway

- `REDIS_URL` est auto-injecté par Railway quand on ajoute un Redis add-on
- `PORT` est auto-injecté par Railway (pas besoin de le définir, uvicorn le bind automatiquement)
- Toutes les env vars se configurent dans Railway dashboard > Variables

## Notes Vercel

- Seules les variables préfixées `NEXT_PUBLIC_` sont accessibles côté client
- `NEXT_PUBLIC_API_URL` doit pointer vers l'URL Railway en production

---

*Dernière mise à jour : mars 2026*
