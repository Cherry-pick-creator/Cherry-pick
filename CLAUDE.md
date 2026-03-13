# CLAUDE.md — Instructions pour Claude Code

> Ce fichier est lu EN PREMIER par Claude Code avant toute action.
> Il définit les règles absolues de travail sur le repo cherrypick-engine.

---

## 1. COMPRENDRE LE PROJET AVANT DE CODER

**Lis ces fichiers dans cet ordre avant d'écrire une seule ligne de code :**

1. `docs/CONTEXT.md` — comprendre pourquoi ce projet existe
2. `docs/ARCH.md` — comprendre la structure technique
3. `docs/SPEC.md` — comprendre chaque fonctionnalité
4. `docs/API.md` — comprendre chaque endpoint
5. `docs/INTEGRATIONS.md` — comprendre les services externes
6. `docs/QUEUE.md` — comprendre les tasks Celery
7. `docs/MIGRATIONS.md` — comprendre le schéma DB

**Lis le skill pertinent avant de coder un module spécifique :**
- Backend FastAPI → `.claude/skills/fastapi.md`
- Tasks Celery → `.claude/skills/celery-redis.md`
- Supabase → `.claude/skills/supabase.md`
- Frontend Next.js → `.claude/skills/nextjs.md`
- Appels fal.ai → `.claude/skills/fal-ai.md`
- Text overlay → `.claude/skills/ffmpeg-overlay.md`

---

## 2. RÈGLES ABSOLUES

### Ne jamais faire

- Ne JAMAIS coder sans avoir lu les specs pertinentes
- Ne JAMAIS inventer un endpoint qui n'est pas dans `docs/API.md`
- Ne JAMAIS inventer une table qui n'est pas dans `docs/MIGRATIONS.md`
- Ne JAMAIS hardcoder des prompts, palettes, fonts — tout est dans la table `personas`
- Ne JAMAIS ajouter de dépendance sans demander confirmation
- Ne JAMAIS modifier le schéma DB sans mettre à jour `docs/MIGRATIONS.md`
- Ne JAMAIS commit des secrets (.env, API keys, tokens)
- Ne JAMAIS utiliser `print()` — utiliser le logger structuré (voir `docs/CONVENTIONS.md`)

### Toujours faire

- Toujours suivre les patterns définis dans `.claude/skills/`
- Toujours ajouter le error handling (voir `docs/ERRORS.md`)
- Toujours typer les fonctions Python (type hints) et TypeScript (interfaces)
- Toujours écrire les Pydantic models pour validation
- Toujours utiliser les variables d'environnement via `app/config.py` (jamais d'accès direct à `os.environ`)
- Toujours séparer la logique métier (services/) des tasks Celery (tasks/) des routes API (api/)
- Toujours retourner des réponses JSON structurées avec les codes HTTP corrects

---

## 3. ARCHITECTURE — RÉSUMÉ RAPIDE

```
cherrypick-engine/
├── backend/           # FastAPI + Celery + Redis → Railway
│   └── app/
│       ├── api/       # Routes REST (ne contient PAS de logique métier)
│       ├── tasks/     # Tasks Celery (appellent les services, gèrent les retries)
│       └── services/  # Logique métier pure (fal.ai, overlay, storage, download)
│
├── frontend/          # Next.js 14 + TypeScript + Tailwind → Vercel
│   └── src/
│       ├── app/       # Pages (App Router)
│       ├── components/ # Composants réutilisables
│       └── lib/       # Client API + types
│
└── docs/              # Specs (ce que tu lis maintenant)
```

**Règle d'or : les routes appellent les tasks, les tasks appellent les services, les services font le travail. Jamais de raccourci.**

---

## 4. CONCEPT CLÉ — MULTI-PERSONA

Ce n'est PAS un outil pour un seul personnage. C'est une plateforme de production vidéo pour **n'importe quel AI influencer**.

Chaque persona a :
- Ses prompts image (FLUX)
- Ses prompts vidéo (Kling)
- Sa palette de couleurs
- Sa font pour le text overlay
- Son negative prompt
- Son style vestimentaire, environnement, éclairage

**CherryPick est la première persona. Pas la seule.**

Conséquence : RIEN n'est hardcodé. Tout vient de la table `personas` en DB. Quand un utilisateur crée un job, il sélectionne une persona. Les prompts, couleurs, fonts sont injectés dynamiquement.

---

## 5. STACK TECHNIQUE

| Composant | Technologie | Version |
|-----------|------------|---------|
| Backend API | FastAPI | 0.110+ |
| Task Queue | Celery | 5.3+ |
| Broker | Redis | 7+ |
| Database | Supabase PostgreSQL | — |
| Storage | Supabase Storage | — |
| Frontend | Next.js | 14+ |
| UI | Tailwind CSS | 3.4+ |
| Language backend | Python | 3.12+ |
| Language frontend | TypeScript | 5+ |
| Image generation | fal.ai FLUX 1.1 Pro | — |
| Video generation | fal.ai Kling v2.6 Motion Control | — |
| Video download | yt-dlp | latest |
| Text overlay | FFmpeg + Pillow | — |
| Deploy backend | Railway | — |
| Deploy frontend | Vercel | — |
| Monitoring | Sentry | — |

---

## 6. CONVENTIONS RAPIDES

- **Python** : snake_case, Black formatter, isort, type hints obligatoires
- **TypeScript** : camelCase, Prettier, interfaces (pas de `any`)
- **Fichiers Python** : max 300 lignes. Si plus → split.
- **Fichiers TypeScript** : max 250 lignes. Si plus → split.
- **Commits** : `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Branches** : `feat/xxx`, `fix/xxx`, `refactor/xxx`
- **Imports Python** : stdlib → third-party → local (isort order)
- **Logs** : structurés JSON, avec `job_id` et `persona_id` dans le contexte

Voir `docs/CONVENTIONS.md` pour le détail complet.

---

## 7. QUAND DEMANDER CONFIRMATION

Demande-moi AVANT de :
- Ajouter une nouvelle dépendance (pip ou npm)
- Créer une nouvelle table en DB
- Créer un nouvel endpoint pas dans API.md
- Modifier un endpoint existant
- Changer l'architecture d'un module
- Supprimer du code

Ne demande PAS pour :
- Implémenter ce qui est dans les specs
- Corriger un bug
- Ajouter des tests
- Améliorer le error handling
- Ajouter des logs

---

## 8. ORDRE D'IMPLÉMENTATION RECOMMANDÉ

```
Phase 1 : Fondations
├── 1. Config (config.py, .env, requirements.txt)
├── 2. Schemas Pydantic (schemas.py)
├── 3. Migrations Supabase (tables personas, jobs, assets)
└── 4. Celery setup (celery_app.py)

Phase 2 : Services
├── 5. fal_client.py (FLUX + Kling)
├── 6. downloader.py (yt-dlp)
├── 7. overlay.py (FFmpeg + Pillow)
└── 8. storage.py (Supabase Storage)

Phase 3 : Tasks
├── 9. generate.py (image + vidéo tasks)
├── 10. postprod.py (overlay task)
└── 11. pipeline.py (orchestration chain)

Phase 4 : API
├── 12. routes.py (tous les endpoints)
└── 13. main.py (FastAPI app)

Phase 5 : Frontend
├── 14. Layout + Sidebar
├── 15. Dashboard page
├── 16. Persona CRUD pages
├── 17. Generate page (single + batch)
├── 18. Jobs page (liste + statuts)
└── 19. Library page (vidéos générées)

Phase 6 : Deploy
├── 20. Procfile + railway.toml
├── 21. next.config.js + vercel.json
└── 22. Tests + monitoring
```

---

*Dernière mise à jour : mars 2026*
