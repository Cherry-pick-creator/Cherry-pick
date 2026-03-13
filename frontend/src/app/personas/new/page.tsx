"use client";

import Header from "@/components/layout/Header";
import PersonaForm from "@/components/personas/PersonaForm";

export default function NewPersonaPage() {
  return (
    <div>
      <Header title="Create Persona" />
      <PersonaForm mode="create" />
    </div>
  );
}
