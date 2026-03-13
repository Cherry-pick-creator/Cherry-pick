"use client";

import { useEffect, useState } from "react";
import { fetchJson } from "@/lib/api";
import { JobListItem } from "@/lib/types";
import Header from "@/components/layout/Header";
import JobCard from "@/components/jobs/JobCard";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import EmptyState from "@/components/shared/EmptyState";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(page), per_page: "20" });
    if (statusFilter) params.set("status", statusFilter);

    fetchJson<{ data: JobListItem[]; total: number }>(
      `/jobs?${params.toString()}`,
    )
      .then((res) => {
        setJobs(res.data);
        setTotal(res.total);
      })
      .finally(() => setLoading(false));
  }, [page, statusFilter]);

  const statuses = ["", "pending", "running", "done", "failed"];

  return (
    <div>
      <Header title="Jobs">
        <div className="flex gap-2">
          {statuses.map((s) => (
            <button
              key={s}
              onClick={() => {
                setStatusFilter(s);
                setPage(1);
              }}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-accent-cyan/10 text-accent-cyan"
                  : "text-text-secondary hover:bg-bg-tertiary"
              }`}
            >
              {s || "All"}
            </button>
          ))}
        </div>
      </Header>

      {loading ? (
        <LoadingSpinner />
      ) : jobs.length === 0 ? (
        <EmptyState
          message="No jobs found."
          cta="Generate Video"
          href="/generate"
        />
      ) : (
        <>
          <div className="space-y-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          {/* Pagination */}
          {total > 20 && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-text-secondary hover:bg-bg-tertiary disabled:opacity-30"
              >
                Previous
              </button>
              <span className="text-sm text-text-secondary">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 20 >= total}
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
