/**
 * Media Library Page
 * Main media library with grid/table views and upload.
 */

"use client";

import { useState } from "react";
import { Upload, FolderOpen } from "lucide-react";

import { useMedia } from "@/lib/hooks/useMedia";
import { useMediaStore } from "@/lib/stores/mediaStore";
import { permissions } from "@/lib/utils/permissions";
import { useAuthStore } from "@/lib/stores/authStore";
import { PageHeader } from "@/components/layout/PageHeader";
import { MediaUploadZone } from "@/components/media/MediaUploadZone";
import { MediaGrid } from "@/components/media/MediaGrid";
import { MediaViewToggle } from "@/components/media/MediaViewToggle";
import { FullPageSpinner } from "@/components/ui/FullPageSpinner";
import { RoleGuard } from "@/components/auth/RoleGuard";

export default function MediaPage() {
  const user = useAuthStore((state) => state.user);
  const { viewMode, setViewMode, isUploadPanelOpen, setUploadPanelOpen } =
    useMediaStore();
  const { data, isLoading } = useMedia(1, 20);

  if (isLoading) {
    return <FullPageSpinner message="Loading media library..." />;
  }

  const media = data?.items || [];
  const canUpload = user ? permissions.canUpload(user.role) : false;

  return (
    <div>
      <PageHeader
        title="Media Library"
        description={`${data?.total || 0} items in library`}
      >
        <div className="flex items-center gap-3">
          <MediaViewToggle current={viewMode} onChange={setViewMode} />
          {canUpload && (
            <button
              onClick={() => setUploadPanelOpen(!isUploadPanelOpen)}
              className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded-md transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span>Upload</span>
            </button>
          )}
        </div>
      </PageHeader>

      {/* Upload zone */}
      {isUploadPanelOpen && canUpload && (
        <MediaUploadZone onClose={() => setUploadPanelOpen(false)} />
      )}

      {/* Empty state */}
      {media.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <FolderOpen className="w-16 h-16 text-text-tertiary mb-4" />
          <h3 className="text-lg font-medium text-text-primary mb-2">
            No media uploaded
          </h3>
          <p className="text-text-secondary max-w-md">
            Upload media files to get started with analysis and processing.
          </p>
          {canUpload && (
            <button
              onClick={() => setUploadPanelOpen(true)}
              className="mt-6 px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded-md transition-colors"
            >
              Upload your first file
            </button>
          )}
        </div>
      )}

      {/* Media grid */}
      {media.length > 0 && viewMode === "grid" && <MediaGrid media={media} />}

      {/* Media table - simplified for now */}
      {media.length > 0 && viewMode === "table" && (
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-surface-raised border-b border-border">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Size
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {media.map((item) => (
                <tr key={item.id} className="hover:bg-surface-raised/50">
                  <td className="px-4 py-3 text-sm text-text-primary">
                    {item.original_filename}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-mono uppercase text-text-secondary bg-surface-raised px-2 py-1 rounded">
                      {item.mime_type.split("/")[1]}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs font-medium uppercase ${
                        item.processing_status === "ready"
                          ? "text-success"
                          : item.processing_status === "failed"
                          ? "text-error"
                          : item.processing_status === "processing"
                          ? "text-status-processing"
                          : "text-text-secondary"
                      }`}
                    >
                      {item.processing_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary font-mono">
                    {item.file_size_bytes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
