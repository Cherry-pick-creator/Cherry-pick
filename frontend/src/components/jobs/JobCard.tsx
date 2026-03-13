"use client";

import Link from "next/link";
import { JobListItem } from "@/lib/types";
import JobStatusBadge from "./JobStatusBadge";

interface Props {
  job: JobListItem;
}

export default function JobCard({ job }: Props) {
  return (
    <Link
      href={`/jobs/${job.id}`}
      className="block rounded-lg border border-border bg-bg-secondary p-4 transition-colors hover:bg-bg-tertiary"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="truncate text-sm font-medium text-text-primary">
            {job.hook_text}
          </p>
          <p className="mt-1 text-xs text-text-secondary">
            {job.persona_name} &middot; {job.type}
          </p>
        </div>
        <JobStatusBadge status={job.status} currentStep={job.current_step} />
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-text-secondary">
        <span className="font-mono">
          {new Date(job.created_at).toLocaleDateString()}{" "}
          {new Date(job.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </Link>
  );
}
