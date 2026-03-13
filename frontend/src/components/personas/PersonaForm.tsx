"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchJson } from "@/lib/api";
import { Persona, PersonaCreate } from "@/lib/types";

interface Props {
  persona?: Persona;
  mode: "create" | "edit";
}

export default function PersonaForm({ persona, mode }: Props) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [name, setName] = useState(persona?.name || "");
  const [description, setDescription] = useState(persona?.description || "");
  const [promptImageBase, setPromptImageBase] = useState(
    persona?.prompt_image_base || "",
  );
  const [promptVideo, setPromptVideo] = useState(persona?.prompt_video || "");
  const [negativePrompt, setNegativePrompt] = useState(
    persona?.negative_prompt || "",
  );
  const [fontFamily, setFontFamily] = useState(
    persona?.font_family || "Bebas Neue",
  );
  const [styleNotes, setStyleNotes] = useState(persona?.style_notes || "");

  // Palette
  const [primary, setPrimary] = useState(persona?.palette.primary || "#0A0A0A");
  const [accent1, setAccent1] = useState(persona?.palette.accent1 || "#00E5FF");
  const [accent2, setAccent2] = useState(persona?.palette.accent2 || "#8B5CF6");
  const [textColor, setTextColor] = useState(
    persona?.palette.text_color || "#F5F0EB",
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");

    const payload: PersonaCreate = {
      name,
      description: description || undefined,
      prompt_image_base: promptImageBase,
      prompt_video: promptVideo,
      negative_prompt: negativePrompt || undefined,
      font_family: fontFamily,
      style_notes: styleNotes || undefined,
      palette: {
        primary,
        accent1,
        accent2,
        text_color: textColor,
        bg_color: primary,
      },
    };

    try {
      if (mode === "create") {
        await fetchJson("/personas", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      } else if (persona) {
        await fetchJson(`/personas/${persona.id}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      }
      router.push("/personas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSaving(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-secondary focus:border-accent-cyan focus:outline-none";
  const labelClass = "block text-sm font-medium text-text-secondary mb-1";

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-5">
      {error && (
        <div className="rounded-lg bg-red-900/30 px-4 py-3 text-sm text-error">
          {error}
        </div>
      )}

      <div>
        <label className={labelClass}>Name *</label>
        <input
          className={inputClass}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. CherryPick"
          required
          minLength={3}
          maxLength={50}
        />
      </div>

      <div>
        <label className={labelClass}>Description</label>
        <input
          className={inputClass}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Short description of this persona"
          maxLength={500}
        />
      </div>

      <div>
        <label className={labelClass}>Image Prompt (FLUX) *</label>
        <textarea
          className={`${inputClass} h-28`}
          value={promptImageBase}
          onChange={(e) => setPromptImageBase(e.target.value)}
          placeholder="Base prompt for FLUX image generation..."
          required
          maxLength={2000}
        />
      </div>

      <div>
        <label className={labelClass}>Video Prompt (Kling) *</label>
        <textarea
          className={`${inputClass} h-20`}
          value={promptVideo}
          onChange={(e) => setPromptVideo(e.target.value)}
          placeholder="Prompt for Kling video generation..."
          required
          maxLength={1000}
        />
      </div>

      <div>
        <label className={labelClass}>Negative Prompt</label>
        <textarea
          className={`${inputClass} h-16`}
          value={negativePrompt}
          onChange={(e) => setNegativePrompt(e.target.value)}
          placeholder="What to avoid in generation..."
          maxLength={1000}
        />
      </div>

      <div>
        <label className={labelClass}>Palette</label>
        <div className="flex gap-4">
          {[
            { label: "Primary", value: primary, set: setPrimary },
            { label: "Accent 1", value: accent1, set: setAccent1 },
            { label: "Accent 2", value: accent2, set: setAccent2 },
            { label: "Text", value: textColor, set: setTextColor },
          ].map((c) => (
            <div key={c.label} className="flex items-center gap-2">
              <input
                type="color"
                value={c.value}
                onChange={(e) => c.set(e.target.value)}
                className="h-8 w-8 cursor-pointer rounded border-0 bg-transparent"
              />
              <span className="text-xs text-text-secondary">{c.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <label className={labelClass}>Font Family</label>
        <input
          className={inputClass}
          value={fontFamily}
          onChange={(e) => setFontFamily(e.target.value)}
          placeholder="Bebas Neue"
        />
      </div>

      <div>
        <label className={labelClass}>Style Notes</label>
        <textarea
          className={`${inputClass} h-16`}
          value={styleNotes}
          onChange={(e) => setStyleNotes(e.target.value)}
          placeholder="Free-form style notes..."
          maxLength={1000}
        />
      </div>

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-accent-cyan px-5 py-2.5 text-sm font-semibold text-black hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : mode === "create"
              ? "Create Persona"
              : "Save Changes"}
        </button>
        <button
          type="button"
          onClick={() => router.push("/personas")}
          className="rounded-lg border border-border px-5 py-2.5 text-sm text-text-secondary hover:bg-bg-tertiary transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
