# Skill: Supabase (Python)

## Client singleton (database.py)
```python
from supabase import create_client
from app.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
```

## CRUD patterns
```python
# SELECT all (with soft delete filter)
result = supabase.table("personas").select("*").is_("deleted_at", "null").order("updated_at", desc=True).execute()
personas = result.data

# SELECT by id
result = supabase.table("personas").select("*").eq("id", persona_id).is_("deleted_at", "null").single().execute()
persona = result.data  # raises if not found

# INSERT
result = supabase.table("personas").insert({"name": "CherryPick", "prompt_image_base": "..."}).execute()
new_persona = result.data[0]

# UPDATE
result = supabase.table("jobs").update({"status": "running"}).eq("id", job_id).execute()

# SOFT DELETE
result = supabase.table("personas").update({"deleted_at": datetime.utcnow().isoformat()}).eq("id", persona_id).execute()

# COUNT
result = supabase.table("jobs").select("id", count="exact").eq("persona_id", pid).in_("status", ["pending", "running"]).execute()
running_count = result.count
```

## Storage patterns
```python
# Upload
supabase.storage.from_("assets").upload(
    path=f"{persona_id}/{job_id}/image_{timestamp}.png",
    file=file_bytes,
    file_options={"content-type": "image/png"}
)

# Get public URL
url = supabase.storage.from_("assets").get_public_url(path)

# Download
data = supabase.storage.from_("assets").download(path)

# Delete
supabase.storage.from_("assets").remove([path])
```

## Règles
- Toujours utiliser `SUPABASE_SERVICE_KEY` (pas anon key) côté backend
- Toujours filtrer `deleted_at IS NULL` sur les SELECT (soft delete)
- Toujours gérer les erreurs (try/except sur les requêtes)
- Pas d'ORM, pas de SQLAlchemy — utiliser le client Supabase directement
