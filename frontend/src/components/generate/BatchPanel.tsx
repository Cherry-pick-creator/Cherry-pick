"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchFormData } from "@/lib/api";
import { PersonaListItem, GenerateBatchResponse } from "@/lib/types";

interface BatchItem {
  hook_text: string;
  trend_source: "url" | "upload";
  trend_url: string;
}

interface Props {
  personas: PersonaListItem[];
}

export default function BatchPanel({ personas }: Props) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [personaId, setPersonaId] = useState(personas[0]?.id || "");

  const [items, setItems] = useState<BatchItem[]>([
    { hook_text: "", trend_source: "url", trend_url: "" },
    { hook_text: "", trend_source: "url", trend_url: "" },
  ]);

  function updateItem(index: number, field: keyof BatchItem, value: string) {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item)),
    );
  }

  function addItem() {
    if (items.length >= 10) return;
    setItems((prev) => [
      ...prev,
      { hook_text: "", trend_source: "url", trend_url: "" },
    ]);
  }

  function removeItem(index: number) {
    if (items.length <= 2) return;
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    const formData = new FormData();
    formData.append("persona_id", personaId);
    formData.append("items", JSON.stringify(items));

    try {
      const result = await fetchFormData<GenerateBatchResponse>(
        "/generate/batch",
        formData,
      );
      router.push(`/jobs?batch=${result.batch_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-secondary focus:border-accent-cyan focus:outline-none";

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-5">
      {error && (
        <div className="rounded-lg bg-red-900/30 px-4 py-3 text-sm text-error">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-text-secondary mb-1">
          Persona *
        </label>
        <select
          className={inputClass}
          value={personaId}
          onChange={(e) => setPersonaId(e.target.value)}
          required
        >
          {personas.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-text-secondary">
            Videos ({items.length}/10)
          </label>
          <button
            type="button"
            onClick={addItem}
            disabled={items.length >= 10}
            className="text-xs text-accent-cyan hover:underline disabled:opacity-50"
          >
            + Add video
          </button>
        </div>

        {items.map((item, index) => (
          <div
            key={index}
            className="rounded-lg border border-border bg-bg-secondary p-4 space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-text-secondary">
                Video {index + 1}
              </span>
              {items.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-xs text-error hover:underline"
                >
                  Remove
                </button>
              )}
            </div>
            <input
              className={inputClass}
              value={item.hook_text}
              onChange={(e) => updateItem(index, "hook_text", e.target.value)}
              placeholder="Hook text..."
              required
              minLength={3}
              maxLength={100}
            />
            <input
              className={inputClass}
              value={item.trend_url}
              onChange={(e) => updateItem(index, "trend_url", e.target.value)}
              placeholder="TikTok URL..."
              required
            />
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-accent-violet px-5 py-3 text-sm font-semibold text-white hover:opacity-90 transition-opacity disabled:opacity-50"
      >
        {submitting
          ? "Launching..."
          : `Generate ${items.length} Videos (Batch)`}
      </button>
    </form>
  );
}
