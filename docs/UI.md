# UI.md — Design System Dashboard

---

## Palette

L'UI du dashboard reprend les codes visuels du projet CherryPick mais en version dashboard fonctionnel, pas en version "contenu TikTok".

### Couleurs

| Token | Hex | Usage |
|-------|-----|-------|
| bg-primary | `#0A0A0A` | Background principal |
| bg-secondary | `#141414` | Cards, panels |
| bg-tertiary | `#1E1E1E` | Inputs, hover states |
| border | `#2A2A2A` | Bordures subtiles |
| text-primary | `#F5F0EB` | Texte principal |
| text-secondary | `#9CA3AF` | Texte secondaire (gray-400) |
| accent-cyan | `#00E5FF` | Actions principales, liens, highlights |
| accent-violet | `#8B5CF6` | Actions secondaires, badges |
| success | `#22C55E` | Status done, success |
| warning | `#F59E0B` | Status running, warning |
| error | `#EF4444` | Status failed, errors |
| cherry | `#DC143C` | Logo, accent ponctuel 🍒 |

### Dark mode only. Pas de light mode.

## Typographie

- **Font UI :** Inter (via Google Fonts)
- **Font mono :** JetBrains Mono (pour les IDs, timestamps)
- **Tailles :** Tailwind defaults (text-sm, text-base, text-lg, text-xl, text-2xl)

## Layout

```
┌─────────────────────────────────────────────────┐
│ Sidebar (fixe, 240px)  │  Main content area     │
│                        │                         │
│ 🍒 Engine             │  ┌─────────────────────┐│
│                        │  │ Page header         ││
│ ▸ Dashboard            │  │ (titre + actions)   ││
│ ▸ Personas             │  ├─────────────────────┤│
│ ▸ Generate             │  │                     ││
│ ▸ Jobs                 │  │ Page content        ││
│ ▸ Library              │  │                     ││
│                        │  │                     ││
│                        │  └─────────────────────┘│
└─────────────────────────────────────────────────┘
```

## Composants clés

### Cards
- Background : bg-secondary
- Border : 1px border
- Border-radius : rounded-lg (8px)
- Padding : p-4 ou p-6
- Hover : bg-tertiary

### Status badges
- **Pending :** bg-gray-700 text-gray-300
- **Running :** bg-yellow-900/50 text-warning avec pulse animation
- **Done :** bg-green-900/50 text-success
- **Failed :** bg-red-900/50 text-error

### Boutons
- **Primary :** bg-accent-cyan text-black font-semibold hover:opacity-90
- **Secondary :** bg-transparent border-accent-cyan text-accent-cyan hover:bg-accent-cyan/10
- **Danger :** bg-error/10 text-error hover:bg-error/20

### Empty states
- Icône centrée (lucide-react)
- Message court
- CTA (bouton pour créer/générer)

---

*Dernière mise à jour : mars 2026*
