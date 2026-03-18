/**
 * Utility: Media Utils
 * Helper functions for media type detection and icon/color mapping.
 */

import type { MediaType, ProcessingStatus, SensitivityLevel } from "@/lib/types/media";
import {
  FileImage,
  FileVideo,
  FileText,
  Layers,
  type LucideIcon,
} from "lucide-react";

/**
 * Get MIME type icon component
 */
export function getMimeIcon(mimeType: string): LucideIcon {
  if (mimeType.startsWith("image/")) return FileImage;
  if (mimeType.startsWith("video/")) return FileVideo;
  if (mimeType === "application/pdf") return FileText;
  if (mimeType.includes("frame")) return Layers;
  return FileImage;
}

/**
 * Get color for media type
 */
export function getMediaTypeColor(type: MediaType): string {
  const colors: Record<MediaType, string> = {
    image: "text-type-image bg-type-image/15",
    video: "text-type-video bg-type-video/15",
    pdf: "text-type-pdf bg-type-pdf/15",
    frame: "text-type-frame bg-type-frame/15",
  };
  return colors[type] || colors.image;
}

/**
 * Get color for processing status
 */
export function getStatusColor(status: ProcessingStatus): string {
  const colors: Record<ProcessingStatus, string> = {
    pending: "text-status-pending bg-status-pending/15",
    processing: "text-status-processing bg-status-processing/15",
    ready: "text-status-ready bg-status-ready/15",
    failed: "text-status-failed bg-status-failed/15",
  };
  return colors[status];
}

/**
 * Get display label for processing status
 */
export function getStatusLabel(status: ProcessingStatus): string {
  const labels: Record<ProcessingStatus, string> = {
    pending: "Pending",
    processing: "Processing",
    ready: "Ready",
    failed: "Failed",
  };
  return labels[status];
}

/**
 * Get color for sensitivity level
 */
export function getSensitivityColor(level: SensitivityLevel): string {
  const colors: Record<SensitivityLevel, string> = {
    none: "text-flag-clear bg-flag-clear/15",
    pii: "text-flag-pii bg-flag-pii/15",
    sensitive: "text-flag-sensitive bg-flag-sensitive/15",
  };
  return colors[level];
}

/**
 * Get display label for sensitivity level
 */
export function getSensitivityLabel(level: SensitivityLevel): string {
  const labels: Record<SensitivityLevel, string> = {
    none: "Clear",
    pii: "PII",
    sensitive: "Sensitive",
  };
  return labels[level];
}

/**
 * Detect media type from MIME type
 */
export function detectMediaType(mimeType: string): MediaType {
  if (mimeType.startsWith("image/")) return "image";
  if (mimeType.startsWith("video/")) return "video";
  if (mimeType === "application/pdf") return "pdf";
  if (mimeType.includes("frame")) return "frame";
  return "image";
}

/**
 * Check if file is an image
 */
export function isImage(mimeType: string): boolean {
  return mimeType.startsWith("image/");
}

/**
 * Check if file is a video
 */
export function isVideo(mimeType: string): boolean {
  return mimeType.startsWith("video/");
}

/**
 * Check if file is a PDF
 */
export function isPdf(mimeType: string): boolean {
  return mimeType === "application/pdf";
}

/**
 * Get file extension from MIME type
 */
export function getExtensionFromMime(mimeType: string): string {
  const map: Record<string, string> = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/tiff": "tiff",
    "image/webp": "webp",
    "video/mp4": "mp4",
    "video/quicktime": "mov",
    "video/x-msvideo": "avi",
    "application/pdf": "pdf",
  };
  return map[mimeType] || "bin";
}
