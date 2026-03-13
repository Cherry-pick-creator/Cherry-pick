# CONTEXT.md — Vision & Business

> Pourquoi ce projet existe, pour qui, et où il va.

---

## 1. Le problème

Créer du contenu vidéo pour un AI influencer est un process manuel en 6-8 étapes : trouver une trend, télécharger la vidéo, générer une image (fal.ai FLUX), générer une vidéo (fal.ai Kling), ajouter le text overlay (CapCut), exporter sans watermark, publier. Chaque vidéo prend 40-60 minutes. Pour 7 vidéos/semaine = 4-7h de travail manuel répétitif.

## 2. La solution

Une plateforme web qui automatise toute la chaîne de production vidéo pour AI influencers. Upload une trend, sélectionne un persona, choisis un hook → la plateforme génère l'image, la vidéo, applique le text overlay, et livre le MP4 final prêt à publier. Tout en arrière-plan via des jobs asynchrones.

## 3. Proposition de valeur

- **40-60 min par vidéo → 2 min** (upload trend + sélectionner les options + lancer)
- **Multi-persona** : configure une fois ton personnage (prompts, palette, font, style), réutilise à l'infini
- **Batch** : génère 7 vidéos d'un coup pour la semaine entière
- **Dashboard temps réel** : suis la progression de chaque job
- **Bibliothèque** : retrouve toutes tes vidéos générées, organisées par persona

## 4. Utilisateurs cibles

| Segment | Usage |
|---------|-------|
| Créateurs AI influencer (comme nous avec CherryPick) | Production quotidienne de contenu vidéo AI |
| Agences marketing | Gestion de plusieurs AI personas pour différents clients |
| Indie hackers / solopreneurs | Créer un canal de distribution vidéo automatisé |

## 5. Business model futur

- **Phase actuelle** : outil interne pour CherryPick
- **Phase 2** : SaaS vendable en self-service (freemium + plans payants)
- **Phase 3** : marketplace de personas pré-configurées

Mais le code est architecturé pour le multi-tenant DÈS la V1. Pas de refonte quand on vend.

## 6. Relation avec cherrypick-bible

Le repo `cherrypick-bible` contient la stratégie, le contenu, et le business du personnage CherryPick. Le `cherrypick-engine` est l'outil technique qui produit les vidéos. La bible dit QUOI produire, le engine dit COMMENT le produire automatiquement.

Les prompts FLUX et Kling de la bible servent de seed data pour la première persona (CherryPick) dans le engine. Mais le engine est indépendant — il fonctionne avec n'importe quelle persona.

## 7. Scope V1

**IN scope :**
- CRUD personas (créer, modifier, supprimer des personnages)
- Génération d'images via fal.ai FLUX
- Génération de vidéos via fal.ai Kling Motion Control
- Téléchargement de trends via yt-dlp
- Text overlay automatique (FFmpeg + Pillow)
- Pipeline complet (trend → image → vidéo → overlay → MP4 final)
- Batch (générer N vidéos en une commande)
- Dashboard avec suivi temps réel des jobs
- Bibliothèque des vidéos générées
- Stockage dans Supabase Storage

**OUT of scope V1 :**
- Publication automatique sur TikTok/YouTube/Instagram (V2)
- Multi-tenant / auth users multiples (V2)
- Billing / plans payants (V2)
- Analytics avancés (V2)
- Marketplace de personas (V3)

---

*Dernière mise à jour : mars 2026*
