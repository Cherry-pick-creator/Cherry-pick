# ERRORS.md — Catalogue d'Erreurs

> Chaque code erreur, message, HTTP status, retry strategy.

---

## Format standard des erreurs API

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {} 
}
```

---

## Erreurs Personas

| Code | HTTP | Message | Retry |
|------|------|---------|-------|
| PERSONA_NOT_FOUND | 404 | Persona not found | Non |
| PERSONA_NAME_CONFLICT | 409 | A persona with this name already exists | Non |
| PERSONA_LOCKED | 423 | Cannot modify persona while jobs are running | Non, attendre |
| PERSONA_VALIDATION_ERROR | 422 | Validation error (détails dans `details`) | Non, corriger input |

## Erreurs Generate

| Code | HTTP | Message | Retry |
|------|------|---------|-------|
| INVALID_PERSONA | 404 | Persona not found | Non |
| INVALID_TREND_SOURCE | 422 | trend_source must be "upload" or "url" | Non |
| MISSING_TREND_FILE | 422 | trend_file is required when trend_source is "upload" | Non |
| MISSING_TREND_URL | 422 | trend_url is required when trend_source is "url" | Non |
| TREND_FILE_TOO_LARGE | 422 | File exceeds maximum size of {max}MB | Non |
| TREND_FILE_INVALID_FORMAT | 422 | Only MP4 files are accepted | Non |
| HOOK_TEXT_TOO_SHORT | 422 | hook_text must be at least 3 characters | Non |
| HOOK_TEXT_TOO_LONG | 422 | hook_text must be at most 100 characters | Non |
| BATCH_TOO_SMALL | 422 | Batch must contain at least 2 items | Non |
| BATCH_TOO_LARGE | 422 | Batch must contain at most 10 items | Non |
| INVALID_VARIATION_INDEX | 422 | image_variation index out of range | Non |

## Erreurs Jobs

| Code | HTTP | Message | Retry |
|------|------|---------|-------|
| JOB_NOT_FOUND | 404 | Job not found | Non |
| BATCH_NOT_FOUND | 404 | Batch not found | Non |
| JOB_NOT_CANCELLABLE | 400 | Cannot cancel a completed or failed job | Non |

## Erreurs Services Externes (stockées dans job.error_message)

| Code | Source | Message | Retry auto |
|------|--------|---------|------------|
| FAL_FLUX_TIMEOUT | fal.ai FLUX | Image generation timed out | 1 retry |
| FAL_FLUX_SAFETY | fal.ai FLUX | Prompt rejected by safety filter | Non |
| FAL_FLUX_ERROR | fal.ai FLUX | fal.ai FLUX internal error | 1 retry |
| FAL_FLUX_RATE_LIMIT | fal.ai FLUX | fal.ai rate limit exceeded | 3 retries (backoff) |
| FAL_KLING_TIMEOUT | fal.ai Kling | Video generation timed out (>10min) | Non |
| FAL_KLING_FAILED | fal.ai Kling | Kling generation failed | Non |
| FAL_KLING_RATE_LIMIT | fal.ai Kling | fal.ai rate limit exceeded | 3 retries (backoff) |
| YTDLP_UNAVAILABLE | yt-dlp | Video unavailable or private | Non |
| YTDLP_UNSUPPORTED | yt-dlp | Unsupported URL format | Non |
| YTDLP_TIMEOUT | yt-dlp | Download timed out | 1 retry |
| OVERLAY_FONT_NOT_FOUND | FFmpeg | Font not found, using fallback | N/A (warning) |
| OVERLAY_FFMPEG_ERROR | FFmpeg | FFmpeg processing failed | 1 retry |
| STORAGE_UPLOAD_FAILED | Supabase | Failed to upload file to storage | 2 retries |
| STORAGE_DOWNLOAD_FAILED | Supabase | Failed to download file from storage | 2 retries |

## Erreurs Système

| Code | HTTP | Message | Action |
|------|------|---------|--------|
| INTERNAL_ERROR | 500 | Internal server error | Log + Sentry alert |
| REDIS_UNAVAILABLE | 503 | Redis connection failed | Health check alarm |
| SUPABASE_UNAVAILABLE | 503 | Supabase connection failed | Health check alarm |

---

*Dernière mise à jour : mars 2026*
