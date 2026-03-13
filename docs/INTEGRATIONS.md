# INTEGRATIONS.md — Services Tiers & API Externes

> Chaque service externe : endpoints, auth, rate limits, payloads, timeouts, erreurs, fallbacks.

---

## 1. fal.ai — FLUX 1.1 Pro (Génération d'images)

### Endpoint
- **URL :** `https://fal.run/fal-ai/flux-pro/v1.1`
- **Méthode :** POST (synchrone, réponse en 10-30s)
- **Auth :** Header `Authorization: Key {FAL_KEY}`

### Request payload
```json
{
  "prompt": "A confident young woman wearing...",
  "image_size": { "width": 768, "height": 1344 },
  "num_images": 1,
  "guidance_scale": 7.5,
  "num_inference_steps": 28,
  "seed": 42,
  "safety_tolerance": "5"
}
```

### Response
```json
{
  "images": [
    { "url": "https://fal.media/files/...", "width": 768, "height": 1344 }
  ],
  "seed": 42,
  "prompt": "..."
}
```

### Error handling
| HTTP Code | Signification | Action |
|-----------|---------------|--------|
| 200 | Succès | Télécharger l'image depuis `images[0].url` |
| 422 | Prompt rejeté (safety) | Fail le job, log le prompt |
| 429 | Rate limit | Retry après `Retry-After` header, max 3 retries |
| 500 | Erreur interne fal.ai | Retry 1 fois après 10s |
| Timeout (>60s) | Requête trop longue | Retry 1 fois |

### Pricing
- ~$0.03-$0.05 par image (FLUX 1.1 Pro)

---

## 2. fal.ai — Kling v2.6 Standard Motion Control (Génération vidéo)

### Workflow : asynchrone (submit → poll → result)

**Étape 1 — Submit**
- **URL :** `https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control`
- **Méthode :** POST
- **Auth :** Header `Authorization: Key {FAL_KEY}`

```json
{
  "prompt": "A confident seductive woman in a Venetian mask...",
  "image_url": "https://...",
  "video_url": "https://...",
  "duration": 5,
  "aspect_ratio": "9:16",
  "negative_prompt": "deformed, blurry..."
}
```

**Response :**
```json
{
  "request_id": "abc-123"
}
```

**Étape 2 — Poll status**
- **URL :** `https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control/requests/{request_id}/status`
- **Méthode :** GET
- **Fréquence :** toutes les 10 secondes
- **Timeout max :** 10 minutes

**Response en cours :**
```json
{
  "status": "IN_QUEUE" | "IN_PROGRESS",
  "queue_position": 3
}
```

**Étape 3 — Get result**
- **URL :** `https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control/requests/{request_id}`
- **Méthode :** GET

**Response completed :**
```json
{
  "video": { "url": "https://fal.media/files/..." },
  "seed": 42
}
```

### Error handling
| Situation | Action |
|-----------|--------|
| status = "FAILED" | Fail le job, log l'erreur fal.ai |
| Poll > 10 min sans completion | Fail avec timeout |
| 429 Rate limit | Retry la requête submit après backoff |
| Image URL inaccessible | Fail immédiat |

### Pricing
- ~$0.10-$0.30 par vidéo (Kling v2.6 Standard, 5s)
- ~$0.20-$0.60 par vidéo (10s)

---

## 3. yt-dlp (Téléchargement de trends TikTok)

### Usage
- **Binaire :** installé via `pip install yt-dlp` ou `apt install yt-dlp`
- **Appel :** subprocess Python

### Commande
```bash
yt-dlp -f "best[height<=1080]" --no-watermark -o "/tmp/cherrypick/{job_id}/trend.mp4" "{url}"
```

### Options importantes
- `--max-filesize 50M` — limite la taille
- `--socket-timeout 30` — timeout téléchargement
- `--no-check-certificates` — pour certains CDN TikTok
- `-f "best[height<=1080]"` — max 1080p

### Error handling
| Erreur | Cause | Action |
|--------|-------|--------|
| "Video unavailable" | Vidéo privée ou supprimée | Fail immédiat avec message explicite |
| "Unsupported URL" | URL pas TikTok | Fail immédiat |
| Timeout >30s | CDN lent | Retry 1 fois |
| Fichier >50Mo | Vidéo trop longue/lourde | Fail avec message |

---

## 4. Supabase Storage

### Configuration
- **URL :** `{SUPABASE_URL}/storage/v1`
- **Auth :** Header `apikey: {SUPABASE_SERVICE_KEY}` + `Authorization: Bearer {SUPABASE_SERVICE_KEY}`
- **Bucket :** `assets`
- **Structure path :** `{persona_id}/{job_id}/{type}_{timestamp}.{ext}`

### Opérations

**Upload :**
```python
supabase.storage.from_("assets").upload(path, file_bytes, {"content-type": mime_type})
```

**Get public URL :**
```python
supabase.storage.from_("assets").get_public_url(path)
```

**Download :**
```python
supabase.storage.from_("assets").download(path)
```

**Delete :**
```python
supabase.storage.from_("assets").remove([path])
```

### Limites
- Fichier max : 50 Mo (configurable dans Supabase dashboard)
- Bucket public pour les URLs de preview
- Service key (pas anon key) pour les uploads depuis le backend

---

## 5. Supabase PostgreSQL

### Client Python
- **Library :** `supabase-py`
- **Auth :** Service role key (full access, pas d'anon key)
- **Usage :** CRUD sur les tables personas, jobs, assets, batch_jobs

### Pas d'ORM. Requêtes directes via le client Supabase :
```python
supabase.table("personas").select("*").eq("id", persona_id).single().execute()
supabase.table("jobs").insert({"persona_id": pid, "status": "pending", ...}).execute()
supabase.table("jobs").update({"status": "running"}).eq("id", job_id).execute()
```

---

*Dernière mise à jour : mars 2026*
