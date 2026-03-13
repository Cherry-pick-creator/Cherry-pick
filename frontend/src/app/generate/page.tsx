"use client";

import { useEffect, useState } from "react";
import { fetchJson } from "@/lib/api";
import { PersonaListItem, PersonaListResponse } from "@/lib/types";
import Header from "@/components/layout/Header";
import GenerateForm from "@/components/generate/GenerateForm";
import BatchPanel from "@/components/generate/BatchPanel";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import EmptyState from "@/components/shared/EmptyState";

export default function GeneratePage() {
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<"single" | "batch">("single");

  useEffect(() => {
    fetchJson<PersonaListResponse>("/personas")
      .then((res) => setPersonas(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading..." />;

  if (personas.length === 0) {
    return (
      <div>
        <Header title="Generate" />
        <EmptyState
          message="Create a persona first to start generating."
          cta="Create Persona"
          href="/personas/new"
        />
      </div>
    );
  }

  return (
    <div>
      <Header title="Generate">
        <div className="flex rounded-lg border border-border">
          {(["single", "batch"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                mode === m
                  ? "bg-accent-cyan/10 text-accent-cyan"
                  : "text-text-secondary hover:text-text-primary"
              } ${m === "single" ? "rounded-l-lg" : "rounded-r-lg"}`}
            >
              {m === "single" ? "Single" : "Batch"}
            </button>
          ))}
        </div>
      </Header>

      {mode === "single" ? (
        <GenerateForm personas={personas} />
      ) : (
        <BatchPanel personas={personas} />
      )}
    </div>
  );
}
