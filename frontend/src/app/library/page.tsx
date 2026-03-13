"use client";

import { useEffect, useState } from "react";
import { fetchJson } from "@/lib/api";
import {
  LibraryItem,
  PersonaListItem,
  PersonaListResponse,
} from "@/lib/types";
import Header from "@/components/layout/Header";
import VideoPreview from "@/components/library/VideoPreview";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import EmptyState from "@/components/shared/EmptyState";

export default function LibraryPage() {
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [personaFilter, setPersonaFilter] = useState("");

  useEffect(() => {
    fetchJson<PersonaListResponse>("/personas").then((res) =>
      setPersonas(res.data),
    );
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(page), per_page: "12" });
    if (personaFilter) params.set("persona_id", personaFilter);

    fetchJson<{ data: LibraryItem[]; total: number }>(
      `/library?${params.toString()}`,
    )
      .then((res) => {
        setItems(res.data);
        setTotal(res.total);
      })
      .finally(() => setLoading(false));
  }, [page, personaFilter]);

  async function handleDelete(assetId: string) {
    if (!confirm("Delete this video from the library?")) return;
    try {
      await fetchJson(`/library/${assetId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((i) => i.id !== assetId));
      setTotal((t) => t - 1);
    } catch {
      // ignore
    }
  }

  return (
    <div>
      <Header title="Library">
        <select
          value={personaFilter}
          onChange={(e) => {
            setPersonaFilter(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-border bg-bg-tertiary px-3 py-1.5 text-sm text-text-primary focus:border-accent-cyan focus:outline-none"
        >
          <option value="">All Personas</option>
          {personas.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </Header>

      {loading ? (
        <LoadingSpinner />
      ) : items.length === 0 ? (
        <EmptyState
          message="No videos in your library yet."
          cta="Generate Video"
          href="/generate"
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {items.map((item) => (
              <VideoPreview
                key={item.id}
                item={item}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {total > 12 && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-text-secondary hover:bg-bg-tertiary disabled:opacity-30"
              >
                Previous
              </button>
              <span className="text-sm text-text-secondary">
                Page {page} of {Math.ceil(total / 12)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 12 >= total}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-text-secondary hover:bg-bg-tertiary disabled:opacity-30"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
