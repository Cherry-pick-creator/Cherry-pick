# MIGRATIONS.md — Schéma Base de Données Supabase

> Toutes les tables, colonnes, types, contraintes, indexes, RLS.

---

## Table : personas

```sql
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    prompt_image_base TEXT NOT NULL,
    prompt_image_variations JSONB DEFAULT '[]'::jsonb,
    prompt_video TEXT NOT NULL,
    negative_prompt TEXT DEFAULT '',
    palette JSONB NOT NULL DEFAULT '{
        "primary": "#0A0A0A",
        "accent1": "#00E5FF",
        "accent2": "#8B5CF6",
        "text_color": "#F5F0EB",
        "bg_color": "#0A0A0A"
    }'::jsonb,
    font_family TEXT NOT NULL DEFAULT 'Bebas Neue',
    font_style JSONB NOT NULL DEFAULT '{
        "size": 72,
        "weight": "bold",
        "shadow": true,
        "position": "center"
    }'::jsonb,
    style_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_personas_name ON personas(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_personas_deleted ON personas(deleted_at);
```

---

## Table : jobs

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID NOT NULL REFERENCES personas(id),
    batch_id UUID REFERENCES batch_jobs(id),
    type TEXT NOT NULL CHECK (type IN ('single', 'batch')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'done', 'failed', 'cancelled')),
    current_step TEXT DEFAULT NULL CHECK (current_step IN (NULL, 'trend_ready', 'image_ready', 'video_ready', 'complete')),
    hook_text TEXT NOT NULL,
    trend_url TEXT,
    trend_asset_id UUID REFERENCES assets(id),
    image_asset_id UUID REFERENCES assets(id),
    video_raw_asset_id UUID REFERENCES assets(id),
    video_final_asset_id UUID REFERENCES assets(id),
    celery_task_id TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    image_variation INT,
    video_duration INT DEFAULT 5,
    font_override JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_jobs_persona ON jobs(persona_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_batch ON jobs(batch_id);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
```

---

## Table : assets

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id),
    persona_id UUID NOT NULL REFERENCES personas(id),
    type TEXT NOT NULL CHECK (type IN ('trend', 'image', 'video_raw', 'video_final')),
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    file_size BIGINT,
    mime_type TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_assets_job ON assets(job_id);
CREATE INDEX idx_assets_persona ON assets(persona_id);
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_deleted ON assets(deleted_at);
```

---

## Table : batch_jobs

```sql
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID NOT NULL REFERENCES personas(id),
    total INT NOT NULL,
    completed INT NOT NULL DEFAULT 0,
    failed INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'done', 'partial', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_batch_jobs_persona ON batch_jobs(persona_id);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
```

---

## Trigger : updated_at auto

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_personas_updated BEFORE UPDATE ON personas FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_jobs_updated BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_batch_jobs_updated BEFORE UPDATE ON batch_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## Seed data : CherryPick persona

```sql
INSERT INTO personas (name, description, prompt_image_base, prompt_image_variations, prompt_video, negative_prompt, palette, font_family, font_style, style_notes)
VALUES (
    'CherryPick',
    'AI influencer — dev/indie hacker roast. Venetian mask, sexy but not NSFW, dark backgrounds with neon accents.',
    'A confident young woman wearing an elegant Venetian masquerade mask, black and gold ornate design, looking directly at camera with piercing eyes through the mask. Fitted black dress with subtle cleavage, accentuating her silhouette. Dramatic cinematic lighting with subtle cyan neon accents, dark moody background, studio setting. Professional fashion photography style, shallow depth of field, 9:16 portrait orientation. Hyper-realistic, photographic quality, no text, no watermarks.',
    '[
        "A confident young woman wearing an ornate Venetian masquerade mask in deep burgundy and gold, looking directly at camera with a seductive gaze. Wearing a fitted burgundy bodysuit, subtle neckline. Dramatic side lighting with violet neon rim light, dark studio background. Professional fashion photography, cinematic mood, shallow depth of field, 9:16 portrait. Hyper-realistic, photographic quality, no text, no watermarks.",
        "A confident young woman wearing a sleek black and silver Venetian masquerade mask, looking directly at camera with intensity. Fitted black top with mesh details, accentuating silhouette. Dark environment with cyan neon strip lights in the background. Futuristic tech aesthetic, dramatic lighting, shallow depth of field, 9:16 portrait. Hyper-realistic, photographic quality, no text, no watermarks.",
        "A confident young woman wearing an elegant gold Venetian masquerade mask, standing on a rooftop at night, city lights and neon signs blurred in the background. Black leather jacket over a fitted top showing silhouette. Dramatic backlit cinematic lighting with violet ambient glow, moody atmosphere. Fashion photography style, shallow depth of field, 9:16 portrait. Hyper-realistic, photographic quality, no text, no watermarks.",
        "Close-up portrait of a confident young woman wearing an ornate black and gold Venetian masquerade mask. Only face and upper shoulders visible, bare shoulders with thin strap detail. Intense seductive eye contact through the mask. Dramatic Rembrandt lighting with subtle cyan neon accent on one side, dark background. Studio fashion photography, extreme shallow depth of field, 9:16 portrait. Hyper-realistic, photographic quality, no text, no watermarks.",
        "A confident young woman wearing an elegant Venetian masquerade mask, sitting in a dark setting, legs crossed, one arm resting casually. Fitted dress accentuating curves, subtle cleavage. Dark interior with violet and cyan neon accent lights in background. Editorial fashion photography, cinematic mood, shallow depth of field, 9:16 portrait. Hyper-realistic, photographic quality, no text, no watermarks."
    ]'::jsonb,
    'A confident seductive woman in a Venetian mask performing smooth dance movements. Cinematic lighting with subtle neon accents, dark background. Fluid natural motion, realistic body movement. Professional quality, no artifacts.',
    'cartoon, anime, illustration, painting, drawing, 3D render, CGI, watermark, text, logo, deformed, ugly, blurry, low quality, oversaturated, bright background, smiling broadly, teeth showing, childlike, costume party, carnival, cheap mask, plastic mask, nudity, explicit, NSFW, lingerie, underwear, bikini, corporate suit, blazer, formal business attire',
    '{"primary": "#0A0A0A", "accent1": "#00E5FF", "accent2": "#8B5CF6", "text_color": "#F5F0EB", "bg_color": "#0A0A0A"}'::jsonb,
    'Bebas Neue',
    '{"size": 72, "weight": "bold", "shadow": true, "position": "center"}'::jsonb,
    'Sexy but not NSFW. Dark backgrounds with cyan and violet neon accents. Venetian mask always visible. Vary ethnicity, hair color, and pose between generations.'
);
```

---

## RLS (Row Level Security)

Pas de RLS en V1 (outil interne, pas de multi-tenant). Préparé pour V2 avec une colonne `owner_id` sur chaque table.

---

## Ordre d'exécution des migrations

1. `batch_jobs` (pas de FK)
2. `personas` (pas de FK)
3. `assets` (FK → jobs, personas — mais jobs n'existe pas encore, donc créer sans FK d'abord)
4. `jobs` (FK → personas, batch_jobs, assets)
5. Ajouter les FK manquantes sur assets
6. Triggers updated_at
7. Seed data CherryPick

---

*Dernière mise à jour : mars 2026*
