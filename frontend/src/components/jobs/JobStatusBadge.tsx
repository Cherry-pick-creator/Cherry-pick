"use client";

import { STATUS_COLORS, STEP_LABELS } from "@/lib/constants";

interface Props {
  status: string;
  currentStep?: string | null;
}

export default function JobStatusBadge({ status, currentStep }: Props) {
  const colorClass =
    STATUS_COLORS[status as keyof typeof STATUS_COLORS] ||
    "bg-gray-700 text-gray-300";

  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass}`}
      >
        {status === "running" && (
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-warning" />
        )}
        {status}
      </span>
      {currentStep && status === "running" && (
        <span className="text-xs text-text-secondary">
          {STEP_LABELS[currentStep] || currentStep}
        </span>
      )}
    </div>
  );
}
