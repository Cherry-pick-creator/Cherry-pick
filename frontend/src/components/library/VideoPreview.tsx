"use client";

import { LibraryItem } from "@/lib/types";

interface Props {
  item: LibraryItem;
  onDelete?: (id: string) => void;
}

export default function VideoPreview({ item, onDelete }: Props) {
  const fileSizeMB = item.file_size
    ? (item.file_size / 1024 / 1024).toFixed(1)
    : "?";

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-bg-secondary">
      {/* Video player */}
      <div className="aspect-[9/16] max-h-80 bg-black">
        <video
          src={item.public_url}
          controls
          preload="metadata"
          className="h-full w-full object-contain"
        />
      </div>

      {/* Info */}
      <div className="p-3">
        <p className="truncate text-sm font-medium text-text-primary">
          {item.hook_text || "Untitled"}
        </p>
        <p className="mt-1 text-xs text-text-secondary">
          {item.persona_name} &middot; {fileSizeMB} MB
        </p>
        <p className="mt-0.5 font-mono text-xs text-text-secondary">
          {new Date(item.created_at).toLocaleDateString()}
        </p>

        <div className="mt-3 flex gap-2">
          <a
            href={item.public_url}
            download
            className="flex-1 rounded-lg border border-accent-cyan px-3 py-1.5 text-center text-xs font-medium text-accent-cyan hover:bg-accent-cyan/10 transition-colors"
          >
            Download
          </a>
          {onDelete && (
            <button
              onClick={() => onDelete(item.id)}
              className="rounded-lg border border-error/30 px-3 py-1.5 text-xs text-error hover:bg-error/10 transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
