/**
 * MediaCard Component
 * Single media item card for grid view.
 */

"use client";

import Link from "next/link";
import { AlertTriangle } from "lucide-react";

import { cn } from "@/lib/utils/cn";
import { formatFileSize } from "@/lib/utils/formatters";
import { detectMediaType } from "@/lib/utils/mediaUtils";
import type { MediaItem } from "@/lib/types/media";
import { MediaTypeBadge } from "./MediaTypeBadge";
import { ProcessingStatusBadge } from "./ProcessingStatusBadge";
import { mediaApi } from "@/lib/api/media";

interface MediaCardProps {
  media: MediaItem;
  isSelected?: boolean;
}

export function MediaCard({ media, isSelected = false }: MediaCardProps) {
  const mediaType = detectMediaType(media.mime_type);
  const hasPII = media.pii_flags && Object.keys(media.pii_flags).length > 0;
  const isProcessing = media.processing_status === "processing";

  return (
    <Link
      href={`/media/${media.id}`}
      className={cn(
        "media-card group relative block bg-surface border border-border rounded-lg overflow-hidden",
        isSelected && "selected"
      )}
    >
      {/* Thumbnail */}
      <div className="aspect-video bg-surface-raised relative">
        {/* Actual thumbnail or placeholder */}
        <img
          src={mediaApi.getMediaFileUrl(media.id)}
          alt={media.original_filename}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Show placeholder on error
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />

        {/* Processing overlay */}
        {isProcessing && (
          <div className="absolute inset-0 bg-background/60 flex items-center justify-center">
            <div className="processing-ring w-8 h-8" />
          </div>
        )}

        {/* PII indicator */}
        {hasPII && (
          <div className="absolute top-2 right-2 w-3 h-3 bg-flag-pii rounded-full" title="PII detected" />
        )}

        {/* Sensitivity flag */}
        {media.classification === "sensitive" && (
          <div className="absolute top-2 left-2">
            <AlertTriangle className="w-4 h-4 text-error" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <h3
            className="text-sm font-medium text-text-primary truncate flex-1"
            title={media.original_filename}
          >
            {media.original_filename}
          </h3>
        </div>

        <div className="flex items-center justify-between mt-2 gap-2">
          <MediaTypeBadge type={mediaType} size="sm" />
          <ProcessingStatusBadge status={media.processing_status} size="sm" />
        </div>

        <p className="text-xs text-text-tertiary mt-2 font-mono">
          {formatFileSize(media.file_size_bytes)}
        </p>
      </div>
    </Link>
  );
}
