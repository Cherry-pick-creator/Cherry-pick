"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchJson } from "@/lib/api";
import { PersonaListItem, JobListItem, LibraryItem } from "@/lib/types";
import Header from "@/components/layout/Header";
import JobCard from "@/components/jobs/JobCard";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

interface DashboardData {
  personaCount: number;
  jobsToday: number;
  jobsThisWeek: number;
  activeJobs: JobListItem[];
  recentVideos: LibraryItem[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [personasRes, activeJobsRes, recentJobsRes, libraryRes] =
          await Promise.all([
            fetchJson<{ data: PersonaListItem[]; total: number }>("/personas"),
            fetchJson<{ data: JobListItem[]; total: number }>(
              "/jobs?status=running&per_page=5",
            ),
            fetchJson<{ data: JobListItem[]; total: number }>(
              "/jobs?per_page=100",
            ),
            fetchJson<{ data: LibraryItem[]; total: number }>(
              "/library?per_page=5",
            ),
          ]);

        const now = new Date();
        const todayStart = new Date(
          now.getFullYear(),
          now.getMonth(),
          now.getDate(),
        );
        const weekStart = new Date(todayStart);
        weekStart.setDate(weekStart.getDate() - weekStart.getDay());

        const jobsToday = recentJobsRes.data.filter(
          (j) => new Date(j.created_at) >= todayStart,
        ).length;
        const jobsThisWeek = recentJobsRes.data.filter(
          (j) => new Date(j.created_at) >= weekStart,
        ).length;

        setData({
          personaCount: personasRes.total,
          jobsToday,
          jobsThisWeek,
          activeJobs: activeJobsRes.data,
          recentVideos: libraryRes.data,
        });
      } catch {
        setData({
          personaCount: 0,
          jobsToday: 0,
          jobsThisWeek: 0,
          activeJobs: [],
          recentVideos: [],
        });
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;
  if (!data) return null;

  const stats = [
    { label: "Personas", value: data.personaCount, href: "/personas" },
    { label: "Jobs today", value: data.jobsToday, href: "/jobs" },
    { label: "Jobs this week", value: data.jobsThisWeek, href: "/jobs" },
  ];

  return (
    <div>
      <Header title="Dashboard" />

      {/* Stats */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <Link
            key={stat.label}
            href={stat.href}
            className="rounded-lg border border-border bg-bg-secondary p-5 transition-colors hover:bg-bg-tertiary"
          >
            <p className="text-sm text-text-secondary">{stat.label}</p>
            <p className="mt-1 text-3xl font-bold text-text-primary">
              {stat.value}
            </p>
          </Link>
        ))}
      </div>

      {/* Active jobs */}
      <div className="mb-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">
            Active Jobs
          </h2>
          <Link
            href="/jobs"
            className="text-sm text-accent-cyan hover:underline"
          >
            View all
          </Link>
        </div>
        {data.activeJobs.length === 0 ? (
          <p className="text-sm text-text-secondary">No active jobs.</p>
        ) : (
          <div className="space-y-2">
            {data.activeJobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>

      {/* Recent videos */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">
            Recent Videos
          </h2>
          <Link
            href="/library"
            className="text-sm text-accent-cyan hover:underline"
          >
            View all
          </Link>
        </div>
        {data.recentVideos.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No videos generated yet.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
            {data.recentVideos.map((video) => (
              <div
                key={video.id}
                className="overflow-hidden rounded-lg border border-border bg-bg-secondary"
              >
                <div className="aspect-[9/16] bg-black">
                  <video
                    src={video.public_url}
                    preload="metadata"
                    className="h-full w-full object-contain"
                  />
                </div>
                <div className="p-2">
                  <p className="truncate text-xs text-text-primary">
                    {video.hook_text}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
