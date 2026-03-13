# 🍒 CherryPick Engine

> Plateforme de production vidéo automatisée pour AI influencers.
> Upload une trend, sélectionne un persona, écris un hook → vidéo finale prête à publier.

## Stack

| Composant | Technologie | Déploiement |
|-----------|------------|-------------|
| Backend API | FastAPI + Celery + Redis | Railway |
| Frontend | Next.js 14 + TypeScript + Tailwind | Vercel |
| Database | Supabase PostgreSQL | Supabase |
| Storage | Supabase Storage | Supabase |
| Image AI | fal.ai FLUX 1.1 Pro | API |
| Video AI | fal.ai Kling v2.6 Motion Control | API |
| Overlay | FFmpeg + Pillow | Railway (worker) |

## Concept clé — Multi-Persona

Ce n'est pas un outil pour un seul personnage. Chaque persona a ses propres prompts, palette, font, style. CherryPick est la première persona configurée, pas la seule. À terme c'est un produit vendable.

## Pipeline

```
Trend TikTok + Persona + Hook text
    │
    ├── 1. Download trend (yt-dlp)
    ├── 2. Generate image (FLUX)
    ├── 3. Generate video (Kling Motion Control)
    └── 4. Text overlay (FFmpeg) → MP4 final prêt à publier
```

Tout tourne en arrière-plan via Celery + Redis. Le dashboard affiche le statut en temps réel.

## Documentation

Toutes les specs sont dans `docs/` :

| Fichier | Contenu |
|---------|---------|
| `CLAUDE.md` | Instructions Claude Code (racine) |
| `docs/CONTEXT.md` | Vision & business |
| `docs/SPEC.md` | Specs fonctionnelles |
| `docs/ARCH.md` | Architecture technique |
| `docs/API.md` | Endpoints REST |
| `docs/INTEGRATIONS.md` | Services tiers (fal.ai, yt-dlp, Supabase) |
| `docs/QUEUE.md` | Tasks Celery/Redis |
| `docs/ENV.md` | Variables d'environnement |
| `docs/MIGRATIONS.md` | Schéma DB Supabase |
| `docs/ERRORS.md` | Catalogue erreurs |
| `docs/SECURITY.md` | Sécurité |
| `docs/CONVENTIONS.md` | Standards de code |
| `docs/UI.md` | Design system dashboard |
| `docs/COPY.md` | Textes UI |
| `docs/TESTS.md` | Stratégie tests |
| `docs/DEPLOY.md` | Config déploiement |
| `docs/MONITORING.md` | Alertes & logs |
| `docs/ANALYTICS.md` | Events tracking |
| `docs/BACKUP.md` | Backup/restore |
| `docs/TASKS.md` | Gestion tâches dev |
| `docs/CHANGELOG.md` | Versioning |
| `docs/ROADMAP.md` | Évolutions V1/V2/V3 |

Skills Claude Code dans `.claude/skills/` (6 fichiers).

## Scope V1

- ✅ CRUD personas (multi-persona)
- ✅ Génération image (FLUX) + vidéo (Kling) + overlay (FFmpeg)
- ✅ Pipeline single + batch (2-10 vidéos)
- ✅ Dashboard + job tracking temps réel
- ✅ Bibliothèque vidéos
- ❌ Cross-posting automatique (V2)
- ❌ Multi-tenant / auth (V2)
- ❌ Billing (V2)

## Repos liés

| Repo | Description |
|------|-------------|
| `cherrypick-bible` | Stratégie, contenu, business du personnage CherryPick |
| `cherrypick-engine` | Ce repo — plateforme de production vidéo |

---

> Dernière mise à jour : mars 2026
