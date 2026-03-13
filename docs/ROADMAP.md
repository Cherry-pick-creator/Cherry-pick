# ROADMAP.md — Évolutions

---

## V1 — MVP (actuel)

Production de vidéos pour AI influencers. Multi-persona, batch, dashboard.

| Feature | Status |
|---------|--------|
| CRUD Personas | 🔲 À faire |
| Image generation (FLUX) | 🔲 À faire |
| Video generation (Kling) | 🔲 À faire |
| Trend download (yt-dlp) | 🔲 À faire |
| Text overlay (FFmpeg) | 🔲 À faire |
| Pipeline orchestration | 🔲 À faire |
| Batch generation | 🔲 À faire |
| Dashboard + job tracking | 🔲 À faire |
| Library | 🔲 À faire |
| Deploy Railway + Vercel | 🔲 À faire |

## V2 — Cross-posting & Multi-tenant

| Feature | Description |
|---------|-------------|
| Auto-publish TikTok | Publication automatique via TikTok API |
| Auto-publish YouTube | Publication automatique via YouTube Data API |
| Auto-publish Instagram | Publication automatique via Instagram Graph API |
| Auth (Supabase Auth) | Login/signup, chaque user a ses personas |
| Multi-tenant | RLS, isolation des données par user |
| Billing | Plans payants, Stripe integration |
| Scheduling | Planifier les publications à l'avance |
| Analytics intégrés | Métriques de chaque vidéo (vues, engagement) post-publication |

## V3 — Marketplace & Scale

| Feature | Description |
|---------|-------------|
| Marketplace de personas | Vendre/partager des personas pré-configurées |
| Templates de hooks | Bibliothèque de hooks par niche |
| AI hook generator | Claude API pour générer des hooks automatiquement |
| Multi-format | Supporter d'autres formats que 9:16 (1:1 pour IG feed, 16:9 pour YouTube long) |
| Custom models | Supporter d'autres modèles que FLUX/Kling (Runway, Pika, etc.) |
| White-label | Version rebranded pour les agences |
| API publique | Permettre l'intégration par des tiers |

---

*Dernière mise à jour : mars 2026*
