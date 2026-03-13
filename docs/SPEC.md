# SPEC.md — Spécifications Fonctionnelles

> Chaque fonctionnalité décrite avec inputs, outputs, edge cases et acceptance criteria.

---

## Feature 1 — CRUD Personas

### Créer une persona

**Input :**
- name (string, unique, 3-50 chars)
- description (string, optionnel, max 500 chars)
- prompt_image_base (string, required, max 2000 chars) — le prompt FLUX principal
- prompt_image_variations (array of strings, optionnel) — variantes du prompt
- prompt_video (string, required, max 1000 chars) — le prompt Kling
- negative_prompt (string, optionnel, max 1000 chars)
- palette (object) : { primary, accent1, accent2, text_color, bg_color } — hex codes
- font_family (string, required) — nom de la font (doit exister dans assets/fonts/)
- font_style (object) : { size: int, weight: string, shadow: bool, position: "center"|"top_third"|"bottom_third" }
- style_notes (string, optionnel, max 1000 chars)

**Output :** persona object avec id + created_at

**Edge cases :**
- Nom déjà pris → 409 Conflict
- Prompt vide → 422 Validation Error
- Palette avec hex invalide → 422

**Acceptance criteria :**
- La persona apparaît dans la liste
- La persona est sélectionnable dans le formulaire de génération
- Les prompts sont utilisés quand on génère avec cette persona

### Lister les personas

**Output :** array de personas triées par updated_at desc

### Modifier une persona

**Input :** mêmes champs que création, tous optionnels (patch)
**Constraint :** ne peut pas modifier une persona si des jobs sont en cours dessus

### Supprimer une persona

**Constraint :** soft delete (set deleted_at). Les jobs et assets existants restent.
**Constraint :** ne peut pas supprimer si des jobs sont en cours.

---

## Feature 2 — Génération Single

### Description

L'utilisateur sélectionne une persona, fournit un hook text, et fournit une trend (upload fichier OU URL TikTok). Le système génère une image, une vidéo, applique le text overlay, et produit le MP4 final.

### Input

- persona_id (uuid, required)
- hook_text (string, required, 3-100 chars)
- trend_source : "upload" ou "url"
  - Si upload : fichier vidéo (MP4, max 50Mo, max 30s)
  - Si url : URL TikTok (string, validée par regex)
- image_variation (int, optionnel) — index de la variation de prompt à utiliser. Si absent → prompt de base.
- video_duration (int, optionnel, default 5) — durée Kling en secondes (5 ou 10)
- font_override (object, optionnel) — pour override la font_style de la persona pour ce job spécifique

### Output

- job_id (uuid)
- status: "pending"
- message: "Job created successfully"

### Pipeline d'exécution (4 étapes séquentielles)

1. **Download/Upload trend** (5-30s)
   - Si URL → yt-dlp download → crop 5 premières secondes → upload Supabase Storage
   - Si fichier → valider format/taille → upload Supabase Storage
   - Résultat : trend_asset_id

2. **Generate image** (10-30s)
   - Charger persona.prompt_image_base (ou variation si spécifié)
   - Appeler fal.ai FLUX 1.1 Pro
   - Résolution : 768x1344 (9:16)
   - Upload résultat → Supabase Storage
   - Résultat : image_asset_id

3. **Generate video** (3-6 min)
   - Charger persona.prompt_video
   - Appeler fal.ai Kling v2.6 Standard Motion Control
   - Inputs : image_url + trend_video_url
   - Poll toutes les 10s jusqu'à completion
   - Upload résultat → Supabase Storage
   - Résultat : video_raw_asset_id

4. **Post-production** (10-30s)
   - Télécharger video_raw depuis Supabase
   - Charger persona.palette + font_family + font_style
   - Appliquer hook_text en overlay via FFmpeg + Pillow
   - Export MP4 H.264, 1080x1920, sans watermark
   - Upload → Supabase Storage
   - Résultat : video_final_asset_id

### Edge cases

- fal.ai FLUX timeout (>60s) → retry 1 fois → fail
- fal.ai Kling timeout (>10min) → fail avec message explicite
- fal.ai rate limit (429) → retry avec backoff exponentiel, max 3 retries
- yt-dlp URL invalide ou vidéo privée → fail immédiat
- Fichier uploadé pas un MP4 → 422
- Fichier uploadé trop gros (>50Mo) → 422
- Font pas trouvée → utiliser fallback "Arial"
- Job persona_id invalide → 404
- Supabase Storage full → fail avec message

---

## Feature 3 — Génération Batch

### Description

Même chose que single, mais pour N vidéos d'un coup. Chaque vidéo du batch a sa propre trend et son propre hook. Toutes partagent la même persona.

### Input

- persona_id (uuid, required)
- items (array, 2-10 items) :
  - hook_text (string, required)
  - trend_source : "upload" ou "url"
  - trend_file ou trend_url
  - image_variation (int, optionnel)

### Output

- batch_id (uuid)
- job_ids (array of uuid)
- total: N
- status: "pending"

### Comportement

- Crée N jobs individuels + 1 batch_job parent
- Les jobs s'exécutent en parallèle (concurrency Celery configurable, default 3)
- Le batch_job.status se met à jour automatiquement :
  - "running" dès qu'un job démarre
  - "done" quand tous les jobs sont done
  - "partial" si certains sont done et d'autres failed
- Chaque job est indépendant : si un fail, les autres continuent

---

## Feature 4 — Suivi des Jobs

### Liste des jobs

**Input (query params) :**
- persona_id (optionnel) — filtrer par persona
- status (optionnel) — filtrer par status
- type (optionnel) — "single" ou "batch"
- page (int, default 1)
- per_page (int, default 20, max 100)

**Output :** array paginée de jobs avec statut, persona name, hook preview, dates

### Détail d'un job

**Output :** job complet avec :
- Tous les champs
- URLs publiques de chaque asset (trend, image, video_raw, video_final)
- Timeline : timestamps de chaque step
- Si failed : error_message

### Polling

Le frontend poll GET /jobs/{id} toutes les 3 secondes tant que status est "pending" ou "running". Dès que status est "done" ou "failed", arrêter le polling.

---

## Feature 5 — Bibliothèque

### Description

Toutes les vidéos finales générées, navigables et filtrables.

### Fonctionnalités

- Liste des assets de type "video_final", triés par date desc
- Filtre par persona
- Preview vidéo inline (player HTML5)
- Download du MP4
- Suppression (soft delete)
- Metadata affichée : persona, hook_text, date, taille fichier, durée

---

## Feature 6 — Dashboard

### Description

Vue d'ensemble rapide à l'ouverture de l'app.

### Contenu

- Nombre total de personas
- Nombre de jobs aujourd'hui / cette semaine
- Jobs en cours (avec statut temps réel)
- 5 dernières vidéos finales (thumbnail + hook preview)
- Coût estimé du mois (basé sur le nombre de générations × prix moyen fal.ai)

---

*Dernière mise à jour : mars 2026*
