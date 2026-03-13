"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchJson } from "@/lib/api";
import { JobDetail, MessageResponse } from "@/lib/types";
import { POLL_INTERVAL_MS, STEP_LABELS } from "@/lib/constants";
import Header from "@/components/layout/Header";
import JobStatusBadge from "@/components/jobs/JobStatusBadge";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

const STEPS = ["trend_ready", "image_ready", "video_ready", "complete"];

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJson<JobDetail>(`/jobs/${jobId}`)
      .then(setJob)
      .catch(() => router.push("/jobs"))
      .finally(() => setLoading(false));
  }, [jobId, router]);

  // Polling
  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed" || job.status === "cancelled") return;

    const interval = setInterval(async () => {
      try {
        const updated = await fetchJson<JobDetail>(`/jobs/${jobId}`);
        setJob(updated);
        if (
          updated.status === "done" ||
          updated.status === "failed" ||
          updated.status === "cancelled"
        ) {
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [job?.status, jobId]);

  async function handleCancel() {
    if (!confirm("Cancel this job?")) return;
    try {
      await fetchJson<MessageResponse>(`/jobs/${jobId}`, { method: "DELETE" });
      const updated = await fetchJson<JobDetail>(`/jobs/${jobId}`);
      setJob(updated);
    } catch {
      // ignore
    }
  }

  if (loading) return <LoadingSpinner message="Loading job..." />;
  if (!job) return null;

  const currentStepIndex = job.current_step
    ? STEPS.indexOf(job.current_step)
    : -1;

  return (
    <div>
      <Header title={job.hook_text}>
        {(job.status === "pending" || job.status === "running") && (
          <button
            onClick={handleCancel}
            className="rounded-lg border border-error/30 px-4 py-2 text-sm text-error hover:bg-error/10 transition-colors"
          >
            Cancel Job
          </button>
        )}
      </Header>

      {/* Status + meta */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <JobStatusBadge status={job.status} currentStep={job.current_step} />
        <span className="text-sm text-text-secondary">
          {job.persona_name} &middot; {job.type}
        </span>
        <span className="font-mono text-xs text-text-secondary">
          {job.id}
        </span>
      </div>

      {/* Error */}
      {job.error_message && (
        <div className="mb-6 rounded-lg bg-red-900/30 px-4 py-3 text-sm text-error">
          {job.error_message}
        </div>
      )}

      {/* Progress steps */}
      <div className="mb-8">
        <h2 className="mb-3 text-sm font-semibold text-text-secondary">
          Pipeline Progress
        </h2>
        <div className="flex gap-2">
          {STEPS.map((step, i) => {
            const isDone = i <= currentStepIndex;
            const isCurrent = i === currentStepIndex && job.status === "running";

            return (
              <div key={step} className="flex-1">
                <div
                  className={`h-1.5 rounded-full transition-colors ${
                    isDone
                      ? isCurrent
                        ? "animate-pulse bg-warning"
                        : "bg-success"
                      : "bg-bg-tertiary"
                  }`}
                />
                <p
                  className={`mt-1.5 text-xs ${
                    isDone ? "text-text-primary" : "text-text-secondary"
                  }`}
                >
                  {STEP_LABELS[step]}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Assets */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {job.assets.image?.url && (
          <div className="rounded-lg border border-border bg-bg-secondary p-4">
            <p className="mb-2 text-sm font-medium text-text-secondary">
              Generated Image
            </p>
            <img
              src={job.assets.image.url}
              alt="Generated"
              className="w-full rounded-lg"
            />
          </div>
        )}

        {job.assets.video_raw?.url && (
          <div className="rounded-lg border border-border bg-bg-secondary p-4">
            <p className="mb-2 text-sm font-medium text-text-secondary">
              Raw Video
            </p>
            <video
              src={job.assets.video_raw.url}
              controls
              preload="metadata"
              className="w-full rounded-lg"
            />
          </div>
        )}

        {job.assets.video_final?.url && (
          <div className="rounded-lg border border-border bg-bg-secondary p-4">
            <p className="mb-2 text-sm font-medium text-text-secondary">
              Final Video
            </p>
            <video
              src={job.assets.video_final.url}
              controls
              preload="metadata"
              className="w-full rounded-lg"
            />
            <a
              href={job.assets.video_final.url}
              download
              className="mt-3 inline-block rounded-lg bg-accent-cyan px-4 py-2 text-sm font-semibold text-black hover:opacity-90 transition-opacity"
            >
              Download MP4
            </a>
          </div>
        )}

        {job.assets.trend?.url && (
          <div className="rounded-lg border border-border bg-bg-secondary p-4">
            <p className="mb-2 text-sm font-medium text-text-secondary">
              Trend Video
            </p>
            <video
              src={job.assets.trend.url}
              controls
              preload="metadata"
              className="w-full rounded-lg"
            />
          </div>
        )}
      </div>

      {/* Metadata */}
      {(job.metadata.video_duration || job.metadata.generation_cost_usd) && (
        <div className="mt-6 rounded-lg border border-border bg-bg-secondary p-4">
          <h2 className="mb-2 text-sm font-semibold text-text-secondary">
            Metadata
          </h2>
          <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
            {job.metadata.video_duration && (
              <div>
                <p className="text-text-secondary">Duration</p>
                <p className="font-mono text-text-primary">
                  {job.metadata.video_duration}s
                </p>
              </div>
            )}
            {job.metadata.image_seed && (
              <div>
                <p className="text-text-secondary">Image Seed</p>
                <p className="font-mono text-text-primary">
                  {job.metadata.image_seed}
                </p>
              </div>
            )}
            {job.metadata.generation_cost_usd && (
              <div>
                <p className="text-text-secondary">Est. Cost</p>
                <p className="font-mono text-text-primary">
                  ${job.metadata.generation_cost_usd}
                </p>
              </div>
            )}
            {job.metadata.total_time_seconds && (
              <div>
                <p className="text-text-secondary">Total Time</p>
                <p className="font-mono text-text-primary">
                  {Math.round(job.metadata.total_time_seconds)}s
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
