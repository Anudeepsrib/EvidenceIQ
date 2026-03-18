/**
 * Media Detail Page
 * Three-panel layout: file info, preview + vision results, EXIF metadata.
 */

"use client";

import { useParams } from "next/navigation";
import { ArrowLeft, RefreshCw } from "lucide-react";
import Link from "next/link";

import { useMediaItem } from "@/lib/hooks/useMedia";
import { useProcessMedia } from "@/lib/hooks/useProcessing";
import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";
import { formatFileSize, formatDate } from "@/lib/utils/formatters";
import { detectMediaType } from "@/lib/utils/mediaUtils";
import { mediaApi } from "@/lib/api/media";

import { FullPageSpinner } from "@/components/ui/FullPageSpinner";
import { HashDisplay } from "@/components/ui/HashDisplay";
import { SensitiveContentAlert } from "@/components/ui/SensitiveContentAlert";
import { MediaTypeBadge } from "@/components/media/MediaTypeBadge";
import { ProcessingStatusBadge } from "@/components/media/ProcessingStatusBadge";
import { PIIFlagBanner } from "@/components/media/PIIFlagBanner";
import { ExifMetadataPanel } from "@/components/media/ExifMetadataPanel";
import { RedactMetadataButton } from "@/components/media/RedactMetadataButton";
import { PageHeader } from "@/components/layout/PageHeader";

// Mock processing results for now
const mockVisionResults = {
  classification: "photograph",
  description: "An outdoor photograph showing a person walking on a sidewalk with buildings in the background.",
  tags: {
    people_present: true,
    estimated_people_count: 1,
    faces_visible: false,
    text_visible: false,
    location_type: "outdoor",
    time_of_day: "day",
    objects: ["person", "sidewalk", "building"],
    scene_tags: ["street", "urban"],
    sensitive_content_flags: ["none"],
  },
};

export default function MediaDetailPage() {
  const params = useParams();
  const mediaId = params.id as string;
  const user = useAuthStore((state) => state.user);

  const { data: media, isLoading } = useMediaItem(mediaId);
  const processMutation = useProcessMedia();

  const canReprocess = user ? permissions.canReprocess(user.role) : false;

  if (isLoading) {
    return <FullPageSpinner message="Loading media details..." />;
  }

  if (!media) {
    return (
      <div className="text-center py-20">
        <p className="text-text-secondary">Media not found</p>
        <Link href="/media" className="text-accent hover:underline mt-4 inline-block">
          Back to library
        </Link>
      </div>
    );
  }

  const mediaType = detectMediaType(media.mime_type);
  const isRedacted = !!media.redacted_at;
  const sensitiveFlags = mockVisionResults.tags.sensitive_content_flags || ["none"];

  return (
    <div>
      <PageHeader title={media.original_filename}>
        <Link
          href="/media"
          className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to library
        </Link>
      </PageHeader>

      {/* Sensitive Content Alert */}
      <SensitiveContentAlert flags={sensitiveFlags} />

      {/* PII Flag Banner */}
      <PIIFlagBanner piiFlags={media.pii_flags} />

      {/* Three-panel layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left panel - File Info (30%) */}
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-surface border border-border rounded-lg p-4">
            <h3 className="font-medium text-text-primary mb-4">File Information</h3>

            <div className="space-y-4">
              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Type</p>
                <MediaTypeBadge type={mediaType} size="md" />
              </div>

              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Status</p>
                <ProcessingStatusBadge status={media.processing_status} size="md" />
              </div>

              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Uploaded</p>
                <p className="font-mono text-sm text-text-primary">
                  {formatDate(media.upload_timestamp)}
                </p>
              </div>

              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Size</p>
                <p className="font-mono text-sm text-text-primary">
                  {formatFileSize(media.file_size_bytes)}
                </p>
              </div>

              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">SHA256 Hash</p>
                <HashDisplay hash={media.sha256_hash} />
              </div>

              {media.width_px && media.height_px && (
                <div>
                  <p className="text-text-tertiary text-xs uppercase mb-1">Dimensions</p>
                  <p className="font-mono text-sm text-text-primary">
                    {media.width_px} × {media.height_px}
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="mt-6 space-y-2">
              <RedactMetadataButton mediaId={media.id} />

              {canReprocess && (
                <button
                  onClick={() => processMutation.mutate({ id: media.id, force: true })}
                  disabled={processMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-surface-raised hover:bg-surface border border-border text-text-primary rounded-md transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={processMutation.isPending ? "w-4 h-4 animate-spin" : "w-4 h-4"} />
                  <span>Re-process</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Center panel - Preview + Vision Results (45%) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Preview */}
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="aspect-video bg-surface-raised flex items-center justify-center">
              <img
                src={mediaApi.getMediaFileUrl(media.id)}
                alt={media.original_filename}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          </div>

          {/* Vision Results */}
          <div className="bg-surface border border-border rounded-lg p-4">
            <h3 className="font-medium text-text-primary mb-4">Vision Analysis</h3>

            <div className="space-y-4">
              {/* Classification */}
              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Classification</p>
                <p className="text-sm text-text-primary capitalize">
                  {mockVisionResults.classification}
                </p>
              </div>

              {/* Description */}
              <div>
                <p className="text-text-tertiary text-xs uppercase mb-1">Description</p>
                <p className="text-sm text-text-primary">
                  {mockVisionResults.description}
                </p>
              </div>

              {/* Tags */}
              <div>
                <p className="text-text-tertiary text-xs uppercase mb-2">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {mockVisionResults.tags.objects.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-surface-raised text-text-secondary text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel - EXIF Metadata (25%) */}
        <div className="lg:col-span-4">
          <ExifMetadataPanel
            exifData={media.exif_metadata}
            isRedacted={isRedacted}
          />
        </div>
      </div>
    </div>
  );
}
