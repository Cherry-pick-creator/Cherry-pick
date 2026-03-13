# ANALYTICS.md — Events Tracking

---

## Events à tracker (dashboard interne)

Pas de Google Analytics ni de third-party en V1. Les métriques sont calculées depuis les tables Supabase.

### Métriques Dashboard

| Métrique | Source | Calcul |
|----------|--------|--------|
| Total personas | `personas` table | COUNT WHERE deleted_at IS NULL |
| Jobs today | `jobs` table | COUNT WHERE created_at > today midnight |
| Jobs this week | `jobs` table | COUNT WHERE created_at > monday midnight |
| Success rate | `jobs` table | COUNT(done) / COUNT(done + failed) * 100 |
| Avg generation time | `jobs.metadata` | AVG(metadata->>'total_time_seconds') |
| Est. monthly cost | `jobs.metadata` | SUM(metadata->>'generation_cost_usd') for current month |
| Videos in library | `assets` table | COUNT WHERE type='video_final' AND deleted_at IS NULL |

### Events dans les logs (pour monitoring)

| Event | Quand | Données loggées |
|-------|-------|----------------|
| job.created | POST /generate/* | job_id, persona_id, type |
| job.step_completed | Chaque step du pipeline | job_id, step, duration_ms |
| job.completed | Fin du pipeline | job_id, total_time_seconds, cost_usd |
| job.failed | Échec d'une step | job_id, step, error_code, error_message |
| persona.created | POST /personas | persona_id, name |
| persona.deleted | DELETE /personas/{id} | persona_id, name |

---

*Dernière mise à jour : mars 2026*
