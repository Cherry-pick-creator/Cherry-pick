"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchJson } from "@/lib/api";
import { Persona, MessageResponse } from "@/lib/types";
import Header from "@/components/layout/Header";
import PersonaForm from "@/components/personas/PersonaForm";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

export default function EditPersonaPage() {
  const params = useParams();
  const router = useRouter();
  const personaId = params.id as string;

  const [persona, setPersona] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchJson<Persona>(`/personas/${personaId}`)
      .then(setPersona)
      .catch(() => router.push("/personas"))
      .finally(() => setLoading(false));
  }, [personaId, router]);

  async function handleDelete() {
    if (!confirm("Delete this persona? This action cannot be undone.")) return;
    setDeleting(true);
    try {
      await fetchJson<MessageResponse>(`/personas/${personaId}`, {
        method: "DELETE",
      });
      router.push("/personas");
    } catch {
      setDeleting(false);
    }
  }

  if (loading) return <LoadingSpinner message="Loading persona..." />;
  if (!persona) return null;

  return (
    <div>
      <Header title={`Edit: ${persona.name}`}>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="rounded-lg border border-error/30 px-4 py-2 text-sm text-error hover:bg-error/10 transition-colors disabled:opacity-50"
        >
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </Header>
      <PersonaForm persona={persona} mode="edit" />
    </div>
  );
}
