# DEPLOY.md — Configuration Déploiement

---

## Backend → Railway

### Services Railway
2 services dans le même repo via Procfile :
- **web** : FastAPI (uvicorn)
- **worker** : Celery worker

### Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.celery_app worker --loglevel=info --concurrency=$CELERY_CONCURRENCY -Q default,generation,postprod
```

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[services]]
name = "worker"
startCommand = "celery -A app.celery_app worker --loglevel=info --concurrency=3 -Q default,generation,postprod"
```

### Redis add-on
- Ajouter Redis via Railway dashboard → Add-ons
- `REDIS_URL` est auto-injecté

### Variables d'environnement
- Configurer toutes les vars de `docs/ENV.md` dans Railway > Variables
- Railway injecte automatiquement `PORT` et `REDIS_URL`

### Build
- Railway détecte Python via `requirements.txt`
- Installer yt-dlp et ffmpeg : ajouter un `nixpacks.toml` :
```toml
[phases.setup]
aptPkgs = ["ffmpeg"]

[phases.install]
cmds = ["pip install -r requirements.txt"]
```

---

## Frontend → Vercel

### Configuration
- Framework : Next.js (auto-détecté)
- Root directory : `frontend/`
- Build command : `npm run build`
- Output directory : `.next`

### Variables d'environnement Vercel
```
NEXT_PUBLIC_API_URL=https://cherrypick-engine.up.railway.app/api/v1
NEXT_PUBLIC_APP_NAME=CherryPick Engine
```

### Domaine
- Vercel assigne un domaine `.vercel.app` automatiquement
- Ajouter un custom domain plus tard si nécessaire

---

## Supabase

### Setup
1. Créer un projet Supabase
2. Exécuter les migrations SQL de `docs/MIGRATIONS.md` dans le SQL Editor
3. Créer le bucket `assets` en Storage (public read)
4. Copier `SUPABASE_URL` et `SUPABASE_SERVICE_KEY`

### Storage bucket
```sql
-- Dans Supabase SQL Editor
INSERT INTO storage.buckets (id, name, public) VALUES ('assets', 'assets', true);
```

---

*Dernière mise à jour : mars 2026*
