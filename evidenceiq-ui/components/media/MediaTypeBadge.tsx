/**
 * MediaTypeBadge Component
 * Badge showing media type (image, video, pdf, frame).
 */

import { FileImage, FileVideo, FileText, Layers } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { MediaType } from "@/lib/types/media";

interface MediaTypeBadgeProps {
  type: MediaType;
  size?: "sm" | "md" | "lg";
}

const typeConfig: Record<MediaType, { icon: React.ComponentType<{ className?: string }>; label: string; color: string }> = {
  image: { icon: FileImage, label: "Image", color: "text-type-image bg-type-image/15" },
  video: { icon: FileVideo, label: "Video", color: "text-type-video bg-type-video/15" },
  pdf: { icon: FileText, label: "PDF", color: "text-type-pdf bg-type-pdf/15" },
  frame: { icon: Layers, label: "Frame", color: "text-type-frame bg-type-frame/15" },
};

const sizeClasses = {
  sm: "px-2 py-0.5 text-xs gap-1",
  md: "px-2.5 py-1 text-sm gap-1.5",
  lg: "px-3 py-1.5 text-base gap-2",
};

const iconSizes = {
  sm: "w-3 h-3",
  md: "w-4 h-4",
  lg: "w-5 h-5",
};

export function MediaTypeBadge({ type, size = "sm" }: MediaTypeBadgeProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full",
        config.color,
        sizeClasses[size]
      )}
    >
      <Icon className={iconSizes[size]} />
      <span className="uppercase tracking-wider">{config.label}</span>
    </span>
  );
}
