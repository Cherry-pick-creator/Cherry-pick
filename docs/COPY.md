# COPY.md — Textes UI

---

## Navigation (Sidebar)

| Item | Label | Icône (lucide-react) |
|------|-------|---------------------|
| Dashboard | Dashboard | LayoutDashboard |
| Personas | Personas | Users |
| Generate | Generate | Sparkles |
| Jobs | Jobs | ListTodo |
| Library | Library | Film |

## Pages — Titres et descriptions

| Page | Titre | Sous-titre |
|------|-------|-----------|
| Dashboard | Dashboard | Overview of your video production |
| Personas | Personas | Manage your AI characters |
| Personas > New | New Persona | Configure a new AI character |
| Personas > Edit | Edit Persona | Update character settings |
| Generate | Generate | Create videos from trends |
| Generate > Batch | Batch Generate | Create multiple videos at once |
| Jobs | Jobs | Track your generation pipeline |
| Jobs > Detail | Job Detail | Pipeline progress and assets |
| Library | Library | Browse your generated videos |

## Empty States

| Page | Message | CTA |
|------|---------|-----|
| Personas (vide) | No personas yet. Create your first AI character to start generating videos. | Create Persona |
| Jobs (vide) | No jobs yet. Generate your first video to see it here. | Generate Video |
| Library (vide) | Your library is empty. Generated videos will appear here. | Generate Video |
| Jobs (filtered, vide) | No jobs match your filters. | Clear Filters |

## Status Labels

| Status | Label | Couleur |
|--------|-------|---------|
| pending | Pending | gray |
| running | Running | warning (yellow) |
| done | Completed | success (green) |
| failed | Failed | error (red) |
| cancelled | Cancelled | gray |
| partial | Partially Done | warning |

## Pipeline Steps

| Step | Label affiché |
|------|--------------|
| (pending) | Waiting to start |
| trend_ready | Trend downloaded |
| image_ready | Image generated |
| video_ready | Video generated |
| complete | Final video ready |

## Boutons et actions

| Action | Label |
|--------|-------|
| Créer persona | Create Persona |
| Modifier persona | Edit |
| Supprimer persona | Delete |
| Lancer single | Generate Video |
| Lancer batch | Generate Batch |
| Annuler job | Cancel |
| Télécharger vidéo | Download |
| Supprimer asset | Delete |
| Voir détail | View Details |
| Retour | Back |

## Messages de confirmation

| Action | Message |
|--------|---------|
| Delete persona | Are you sure you want to delete this persona? This action cannot be undone. |
| Cancel job | Are you sure you want to cancel this job? |
| Delete asset | Are you sure you want to delete this video? |

## Toasts / Notifications

| Event | Message | Type |
|-------|---------|------|
| Persona créée | Persona "{name}" created successfully | success |
| Persona modifiée | Persona updated | success |
| Persona supprimée | Persona deleted | success |
| Job lancé | Video generation started | success |
| Batch lancé | Batch of {n} videos started | success |
| Job terminé | Video ready! | success |
| Job échoué | Generation failed: {error} | error |
| Job annulé | Job cancelled | info |

---

*Dernière mise à jour : mars 2026*
