/**
 * ProcessingStatusBadge Component
 * Badge showing processing status with appropriate styling.
 */

import { Loader2, CheckCircle, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { ProcessingStatus } from "@/lib/types/media";

interface ProcessingStatusBadgeProps {
  status: ProcessingStatus;
  size?: "sm" | "md";
}

const statusConfig: Record<ProcessingStatus, { icon: React.ComponentType<{ className?: string }>; label: string; color: string }> = {
  pending: { icon: Clock, label: "Pending", color: "text-status-pending bg-status-pending/15" },
  processing: { icon: Loader2, label: "Processing", color: "text-status-processing bg-status-processing/15" },
  ready: { icon: CheckCircle, label: "Ready", color: "text-status-ready bg-status-ready/15" },
  failed: { icon: XCircle, label: "Failed", color: "text-status-failed bg-status-failed/15" },
};

const sizeClasses = {
  sm: "px-2 py-0.5 text-xs gap-1",
  md: "px-2.5 py-1 text-sm gap-1.5",
};

const iconSizes = {
  sm: "w-3 h-3",
  md: "w-4 h-4",
};

export function ProcessingStatusBadge({ status, size = "sm" }: ProcessingStatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full",
        config.color,
        sizeClasses[size]
      )}
    >
      <Icon className={cn(iconSizes[size], status === "processing" && "animate-spin")} />
      <span className="uppercase tracking-wider">{config.label}</span>
    </span>
  );
}
