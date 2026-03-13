"use client";

import Link from "next/link";
import { PersonaListItem } from "@/lib/types";

interface Props {
  persona: PersonaListItem;
}

export default function PersonaCard({ persona }: Props) {
  return (
    <Link
      href={`/personas/${persona.id}`}
      className="block rounded-lg border border-border bg-bg-secondary p-5 transition-colors hover:bg-bg-tertiary"
    >
      {/* Color strip */}
      <div className="mb-3 flex gap-1.5">
        {[
          persona.palette.primary,
          persona.palette.accent1,
          persona.palette.accent2,
        ].map((color, i) => (
          <div
            key={i}
            className="h-2 w-8 rounded-full"
            style={{ backgroundColor: color }}
          />
        ))}
      </div>

      <h3 className="text-lg font-semibold text-text-primary">
        {persona.name}
      </h3>

      {persona.description && (
        <p className="mt-1 line-clamp-2 text-sm text-text-secondary">
          {persona.description}
        </p>
      )}

      <div className="mt-4 flex items-center justify-between text-xs text-text-secondary">
        <span>{persona.font_family}</span>
        <span>
          {persona.job_count} job{persona.job_count !== 1 ? "s" : ""}
        </span>
      </div>
    </Link>
  );
}
