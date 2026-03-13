"use client";

import Link from "next/link";

interface Props {
  message: string;
  cta?: string;
  href?: string;
}

export default function EmptyState({ message, cta, href }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
      <div className="rounded-full bg-bg-secondary p-6">
        <svg className="h-10 w-10 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <p className="text-text-secondary">{message}</p>
      {cta && href && (
        <Link
          href={href}
          className="rounded-lg bg-accent-cyan px-4 py-2 text-sm font-semibold text-black hover:opacity-90 transition-opacity"
        >
          {cta}
        </Link>
      )}
    </div>
  );
}
