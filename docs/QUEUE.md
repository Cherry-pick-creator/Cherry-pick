# QUEUE.md — Tasks Celery / Redis

> Chaque task : signature, params, retries, timeouts, chains, dead letter.

---

## Configuration Celery

```python
broker_url = REDIS_URL
result_backend = REDIS_URL
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
task_track_started = True
task_acks_late = True
worker_prefetch_multiplier = 1
worker_concurrency = 3          # 3 jobs en parallèle max
task_soft_time_limit = 660      # 11 min soft limit
task_time_limit = 720           # 12 min hard limit
```

---

## Tasks

### Task 1 — download_trend

| Param | Type | Description |
|-------|------|-------------|
| job_id | str (uuid) | ID du job |
| trend_source | str | "url" ou "upload" |
| trend_url | str, nullable | URL TikTok à télécharger |
| trend_storage_path | str, nullable | Path si déjà uploadé |

**Queue :** `default`
**Timeout :** 60s
**Retries :** 1 (erreurs réseau uniquement)
**Retry delay :** 10s

**Behaviour :**
1. Si `trend_source == "url"` : yt-dlp download → crop 5s → upload Supabase Storage
2. Si `trend_source == "upload"` : fichier déjà en Storage, juste valider qu'il existe
3. Update job : `current_step = "trend_ready"`, sauvegarder `trend_asset_id`

---

### Task 2 — generate_image

| Param | Type | Description |
|-------|------|-------------|
| job_id | str (uuid) | ID du job |
| persona_id | str (uuid) | ID de la persona |
| image_variation | int, nullable | Index de la variation à utiliser |

**Queue :** `generation`
**Timeout :** 90s
**Retries :** 1 (fal.ai 500 ou timeout uniquement)
**Retry delay :** 15s

**Behaviour :**
1. Charger persona depuis DB
2. Sélectionner le prompt (base ou variation[index])
3. Appeler fal.ai FLUX (voir INTEGRATIONS.md)
4. Télécharger l'image depuis l'URL retournée
5. Upload vers Supabase Storage : `{persona_id}/{job_id}/image_{timestamp}.png`
6. Créer asset en DB, update job : `current_step = "image_ready"`, `image_asset_id`

---

### Task 3 — generate_video

| Param | Type | Description |
|-------|------|-------------|
| job_id | str (uuid) | ID du job |
| persona_id | str (uuid) | ID de la persona |
| video_duration | int | 5 ou 10 secondes |

**Queue :** `generation`
**Timeout :** 660s (11 min — Kling peut prendre jusqu'à 10 min)
**Retries :** 0 (trop coûteux pour retry automatiquement)
**Retry delay :** N/A

**Behaviour :**
1. Charger persona.prompt_video + persona.negative_prompt depuis DB
2. Charger image_url et trend_url depuis le job (assets)
3. Submit vers fal.ai Kling Motion Control
4. Poll toutes les 10s (max 60 polls = 10 min)
5. Télécharger la vidéo depuis l'URL retournée
6. Upload vers Supabase Storage : `{persona_id}/{job_id}/video_raw_{timestamp}.mp4`
7. Créer asset en DB, update job : `current_step = "video_ready"`, `video_raw_asset_id`

---

### Task 4 — postprod

| Param | Type | Description |
|-------|------|-------------|
| job_id | str (uuid) | ID du job |
| persona_id | str (uuid) | ID de la persona |
| hook_text | str | Texte à overlayer |
| font_override | dict, nullable | Override de la font_style |

**Queue :** `postprod`
**Timeout :** 120s
**Retries :** 1
**Retry delay :** 5s

**Behaviour :**
1. Télécharger video_raw depuis Supabase Storage vers /tmp
2. Charger persona.palette, persona.font_family, persona.font_style depuis DB
3. Appliquer font_override si fourni
4. Rendre le text overlay via Pillow (image du texte)
5. Combiner via FFmpeg (overlay sur la vidéo)
6. Export MP4 H.264, 1080x1920, sans watermark
7. Upload vers Supabase Storage : `{persona_id}/{job_id}/video_final_{timestamp}.mp4`
8. Créer asset en DB, update job : `current_step = "complete"`, `status = "done"`, `video_final_asset_id`
9. Nettoyer /tmp/{job_id}/

---

### Task 5 — pipeline_single

Orchestrateur. Chaîne les 4 tasks pour un job single.

```python
from celery import chain

chain(
    download_trend.s(job_id, trend_source, trend_url, trend_storage_path),
    generate_image.s(job_id, persona_id, image_variation),
    generate_video.s(job_id, persona_id, video_duration),
    postprod.s(job_id, persona_id, hook_text, font_override),
).apply_async()
```

**Error handling :** si une task de la chain échoue, les suivantes ne s'exécutent pas. Le job passe en `status = "failed"` avec l'erreur de la task qui a échoué.

---

### Task 6 — pipeline_batch

Lance N pipeline_single en parallèle.

```python
from celery import group

group([
    pipeline_single.s(job_id, persona_id, item)
    for job_id, item in zip(job_ids, items)
]).apply_async()
```

Met à jour le batch_job.completed et batch_job.failed via callbacks.

---

## Queues

| Queue | Tasks | Workers | Usage |
|-------|-------|---------|-------|
| default | download_trend | 3 | Téléchargements rapides |
| generation | generate_image, generate_video | 3 | Appels fal.ai (longs) |
| postprod | postprod | 2 | FFmpeg overlay (CPU) |

---

## Error handling global

Chaque task wrappe son exécution dans un try/except qui :
1. Log l'erreur avec `job_id` dans le contexte
2. Update le job en DB : `status = "failed"`, `error_message = str(error)`
3. Propage l'exception pour que Celery gère le retry si configuré
4. Si max retries atteint → le job reste en "failed"

---

*Dernière mise à jour : mars 2026*
