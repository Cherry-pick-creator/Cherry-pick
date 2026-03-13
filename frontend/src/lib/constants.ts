export const APP_NAME =
  process.env.NEXT_PUBLIC_APP_NAME || "CherryPick Engine";

export const POLL_INTERVAL_MS = 3000;

export const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: "LayoutDashboard" },
  { label: "Personas", href: "/personas", icon: "Users" },
  { label: "Generate", href: "/generate", icon: "Sparkles" },
  { label: "Jobs", href: "/jobs", icon: "ListChecks" },
  { label: "Library", href: "/library", icon: "Film" },
] as const;

export const STATUS_COLORS = {
  pending: "bg-gray-700 text-gray-300",
  running: "bg-yellow-900/50 text-warning",
  done: "bg-green-900/50 text-success",
  failed: "bg-red-900/50 text-error",
  cancelled: "bg-gray-700 text-gray-400",
  partial: "bg-yellow-900/50 text-warning",
} as const;

export const STEP_LABELS: Record<string, string> = {
  trend_ready: "Trend downloaded",
  image_ready: "Image generated",
  video_ready: "Video generated",
  complete: "Post-production done",
};
