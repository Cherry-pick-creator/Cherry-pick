"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchFormData } from "@/lib/api";
import { PersonaListItem, GenerateSingleResponse } from "@/lib/types";

interface Props {
  personas: PersonaListItem[];
}

export default function GenerateForm({ personas }: Props) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [personaId, setPersonaId] = useState(personas[0]?.id || "");
  const [hookText, setHookText] = useState("");
  const [trendSource, setTrendSource] = useState<"url" | "upload">("url");
  const [trendUrl, setTrendUrl] = useState("");
  const [trendFile, setTrendFile] = useState<File | null>(null);
  const [videoDuration, setVideoDuration] = useState(5);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    const formData = new FormData();
    formData.append("persona_id", personaId);
    formData.append("hook_text", hookText);
    formData.append("trend_source", trendSource);
    formData.append("video_duration", String(videoDuration));

    if (trendSource === "url") {
      formData.append("trend_url", trendUrl);
    } else if (trendFile) {
      formData.append("trend_file", trendFile);
    }

    try {
      const result = await fetchFormData<GenerateSingleResponse>(
        "/generate/single",
        formData,
      );
      router.push(`/jobs/${result.job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-secondary focus:border-accent-cyan focus:outline-none";
  const labelClass = "block text-sm font-medium text-text-secondary mb-1";

  return (
    <form onSubmit={handleSubmit} className="max-w-xl space-y-5">
      {error && (
        <div className="rounded-lg bg-red-900/30 px-4 py-3 text-sm text-error">
          {error}
        </div>
      )}

      <div>
        <label className={labelClass}>Persona *</label>
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

      <div>
        <label className={labelClass}>Hook Text *</label>
        <input
          className={inputClass}
          value={hookText}
          onChange={(e) => setHookText(e.target.value)}
          placeholder="Your SaaS solves a problem nobody has"
          required
          minLength={3}
          maxLength={100}
        />
        <p className="mt-1 text-xs text-text-secondary">
          {hookText.length}/100 characters
        </p>
      </div>

      <div>
        <label className={labelClass}>Trend Source *</label>
        <div className="flex gap-3">
          {(["url", "upload"] as const).map((source) => (
            <button
              key={source}
              type="button"
              onClick={() => setTrendSource(source)}
              className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
                trendSource === source
                  ? "border-accent-cyan bg-accent-cyan/10 text-accent-cyan"
                  : "border-border text-text-secondary hover:bg-bg-tertiary"
              }`}
            >
              {source === "url" ? "TikTok URL" : "Upload File"}
            </button>
          ))}
        </div>
      </div>

      {trendSource === "url" ? (
        <div>
          <label className={labelClass}>TikTok URL *</label>
          <input
            className={inputClass}
            value={trendUrl}
            onChange={(e) => setTrendUrl(e.target.value)}
            placeholder="https://www.tiktok.com/@user/video/..."
            required
          />
        </div>
      ) : (
        <div>
          <label className={labelClass}>Trend Video (MP4, max 50MB) *</label>
          <input
            type="file"
            accept="video/mp4"
            onChange={(e) => setTrendFile(e.target.files?.[0] || null)}
            className="text-sm text-text-secondary file:mr-3 file:rounded-lg file:border-0 file:bg-bg-tertiary file:px-3 file:py-2 file:text-sm file:text-text-primary hover:file:bg-border"
            required
          />
        </div>
      )}

      <div>
        <label className={labelClass}>Video Duration</label>
        <div className="flex gap-3">
          {[5, 10].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => setVideoDuration(d)}
              className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
                videoDuration === d
                  ? "border-accent-cyan bg-accent-cyan/10 text-accent-cyan"
                  : "border-border text-text-secondary hover:bg-bg-tertiary"
              }`}
            >
              {d}s
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-accent-cyan px-5 py-3 text-sm font-semibold text-black hover:opacity-90 transition-opacity disabled:opacity-50"
      >
        {submitting ? "Launching..." : "Generate Video"}
      </button>
    </form>
  );
}
