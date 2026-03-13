"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchJson } from "@/lib/api";
import { PersonaListItem, PersonaListResponse } from "@/lib/types";
import Header from "@/components/layout/Header";
import PersonaCard from "@/components/personas/PersonaCard";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import EmptyState from "@/components/shared/EmptyState";

export default function PersonasPage() {
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJson<PersonaListResponse>("/personas")
      .then((res) => setPersonas(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading personas..." />;

  return (
    <div>
      <Header title="Personas">
        <Link
          href="/personas/new"
          className="rounded-lg bg-accent-cyan px-4 py-2 text-sm font-semibold text-black hover:opacity-90 transition-opacity"
        >
          New Persona
        </Link>
      </Header>

      {personas.length === 0 ? (
        <EmptyState
          message="No personas yet."
          cta="Create Persona"
          href="/personas/new"
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {personas.map((p) => (
            <PersonaCard key={p.id} persona={p} />
          ))}
        </div>
      )}
    </div>
  );
}
