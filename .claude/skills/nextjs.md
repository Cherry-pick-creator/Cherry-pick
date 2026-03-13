# Skill: Next.js 14 (App Router)

## Structure des pages
```
src/app/
├── layout.tsx          # Layout racine avec Sidebar
├── page.tsx            # Dashboard
├── personas/
│   ├── page.tsx        # Liste → fetch côté client (useEffect)
│   ├── new/page.tsx    # Formulaire création
│   └── [id]/page.tsx   # Formulaire édition
├── generate/page.tsx   # Formulaire génération
├── jobs/
│   ├── page.tsx        # Liste jobs
│   └── [id]/page.tsx   # Détail job (polling)
└── library/page.tsx    # Bibliothèque
```

## Pattern page avec data fetching
```tsx
"use client";
import { useEffect, useState } from "react";
import { fetchJson } from "@/lib/api";
import { Persona } from "@/lib/types";
import PersonaCard from "@/components/personas/PersonaCard";
import EmptyState from "@/components/shared/EmptyState";

export default function PersonasPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJson<{ data: Persona[] }>("/personas")
      .then((res) => setPersonas(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (personas.length === 0) return <EmptyState message="No personas yet." cta="Create Persona" href="/personas/new" />;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {personas.map((p) => <PersonaCard key={p.id} persona={p} />)}
    </div>
  );
}
```

## Polling pattern (jobs)
```tsx
useEffect(() => {
  if (job.status === "done" || job.status === "failed") return;
  const interval = setInterval(async () => {
    const updated = await fetchJson<Job>(`/jobs/${job.id}`);
    setJob(updated);
    if (updated.status === "done" || updated.status === "failed") clearInterval(interval);
  }, 3000);
  return () => clearInterval(interval);
}, [job.status]);
```

## Règles
- "use client" sur toutes les pages avec state/effects
- Tailwind uniquement pour le styling (pas de CSS modules)
- Types importés depuis `@/lib/types.ts`
- API calls via `@/lib/api.ts` (jamais de fetch direct)
- Pas de `any` dans le TypeScript
- Composants dans `components/` organisés par domaine
