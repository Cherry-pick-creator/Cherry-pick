# SECURITY.md — Sécurité

---

## V1 — Outil interne (pas de multi-tenant)

### Auth
- Pas d'authentification utilisateur en V1 (single user)
- Le backend est protégé par CORS (seul le frontend Vercel peut l'appeler)
- Préparer l'architecture pour ajouter auth en V2 (Supabase Auth)

### CORS
```python
origins = settings.CORS_ORIGINS.split(",")
# Dev: ["http://localhost:3000"]
# Prod: ["https://cherrypick-engine.vercel.app"]
```

### Secrets
- Tous les secrets dans les variables d'environnement (jamais dans le code)
- `.env` dans `.gitignore`
- `SUPABASE_SERVICE_KEY` = full access DB → ne JAMAIS exposer côté frontend
- `FAL_KEY` = accès payant fal.ai → ne JAMAIS exposer côté frontend
- Le frontend n'a accès qu'à `NEXT_PUBLIC_*` variables

### Validation des inputs
- Pydantic valide tous les inputs API côté backend
- Taille max upload : configurable via `MAX_UPLOAD_SIZE_MB`
- Seuls les fichiers MP4 sont acceptés pour les trends
- Les URLs sont validées par regex (TikTok patterns)
- Le hook_text est sanitizé (pas de HTML/JS injection)

### Rate limiting
- Pas de rate limiting en V1 (single user)
- Préparer middleware FastAPI pour V2 (`slowapi`)

### Supabase Storage
- Bucket `assets` en public read (pour les previews)
- Uploads uniquement via service key (backend)
- Le frontend ne peut pas uploader directement vers Supabase

### Railway
- HTTPS automatique (Railway fournit SSL)
- Pas d'accès SSH en production
- Logs accessibles uniquement via Railway dashboard

---

*Dernière mise à jour : mars 2026*
