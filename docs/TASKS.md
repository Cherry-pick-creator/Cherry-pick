# TASKS.md — Gestion des Tâches de Développement

---

## Priorités

| Priorité | Label | Description |
|----------|-------|-------------|
| P0 | Critical | Bloque tout, fix immédiat |
| P1 | High | Feature core, sprint en cours |
| P2 | Medium | Amélioration, prochain sprint |
| P3 | Low | Nice to have |

## Sprints V1

### Sprint 1 — Fondations (semaine 1)
- [x] CLAUDE.md + docs/ complets
- [ ] Setup backend (FastAPI + Celery + Redis)
- [ ] Setup Supabase (tables + storage bucket)
- [ ] Config (config.py, .env)
- [ ] Schemas Pydantic
- [ ] Health check endpoint

### Sprint 2 — Services (semaine 2)
- [ ] fal_client.py (FLUX + Kling)
- [ ] downloader.py (yt-dlp)
- [ ] overlay.py (FFmpeg + Pillow)
- [ ] storage.py (Supabase Storage)
- [ ] Tests unitaires services

### Sprint 3 — Tasks + API (semaine 3)
- [ ] Celery tasks (generate, postprod, pipeline)
- [ ] API endpoints (personas CRUD, generate, jobs, library)
- [ ] Tests API

### Sprint 4 — Frontend (semaine 4)
- [ ] Layout + Sidebar + Navigation
- [ ] Dashboard page
- [ ] Persona CRUD pages
- [ ] Generate page (single + batch)
- [ ] Jobs page + polling
- [ ] Library page

### Sprint 5 — Deploy + Polish (semaine 5)
- [ ] Deploy Railway (backend + worker)
- [ ] Deploy Vercel (frontend)
- [ ] Sentry setup
- [ ] Seed CherryPick persona
- [ ] Tests end-to-end manuels
- [ ] Bug fixes

---

*Dernière mise à jour : mars 2026*
