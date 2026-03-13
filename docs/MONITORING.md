# MONITORING.md — Alertes & Logs

---

## Sentry

### Setup
- `pip install sentry-sdk[fastapi]`
- Init dans `main.py` :
```python
import sentry_sdk
sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1, environment=settings.APP_ENV)
```

### Alertes
- Toutes les exceptions non catchées → Sentry automatiquement
- Tasks Celery qui fail → alert Sentry
- fal.ai timeouts répétés (>3 en 1h) → alert

## Logs structurés

Format JSON :
```json
{
  "timestamp": "2026-03-01T14:30:00Z",
  "level": "INFO",
  "message": "Image generation completed",
  "job_id": "uuid",
  "persona_id": "uuid",
  "duration_ms": 15230,
  "service": "fal_client"
}
```

Configurer dans `main.py` :
```python
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {"timestamp": self.formatTime(record), "level": record.levelname, "message": record.getMessage()}
        if hasattr(record, "job_id"): log["job_id"] = record.job_id
        return json.dumps(log)
```

## Health check

`GET /api/v1/health` vérifie :
- API up
- Redis connected (ping)
- Supabase connected (simple query)

Configurer un uptime monitor (UptimeRobot ou Railway built-in) qui ping `/health` toutes les 5 min.

## Métriques à suivre

| Métrique | Source | Seuil d'alerte |
|----------|--------|---------------|
| Jobs failed / heure | DB query | > 5 |
| Temps moyen génération | job.metadata | > 8 min |
| fal.ai errors / heure | Sentry | > 10 |
| Storage usage | Supabase dashboard | > 4 Go |
| Redis memory | Railway metrics | > 80% |

---

*Dernière mise à jour : mars 2026*
