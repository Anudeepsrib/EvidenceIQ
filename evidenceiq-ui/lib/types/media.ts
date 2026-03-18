/**
 * Media Types
 * TypeScript interfaces for media items, tags, and API responses.
 */

export type MediaType = "image" | "video" | "pdf" | "frame";
export type ProcessingStatus = "pending" | "processing" | "ready" | "failed";
export type SensitivityLevel = "none" | "pii" | "sensitive";

export interface MediaItem {
  id: string;
  uuid: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  width_px: number | null;
  height_px: number | null;
  duration_seconds: number | null;
  parent_id: string | null;
  uploaded_by: string;
  upload_timestamp: string;
  processing_status: ProcessingStatus;
  classification: string | null;
  description: string | null;
  exif_metadata: Record<string, unknown> | null;
  pii_flags: Record<string, unknown> | null;
  model_used: string | null;
  processed_at: string | null;
  redacted_at: string | null;
  children_count: number;
}

export interface MediaTag {
  id: string;
  media_id: string;
  tag_type: "object" | "scene" | "concept" | "custom";
  tag_value: string;
  confidence: number | null;
}

export interface MediaUploadResponse {
  id: string;
  uuid: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  processing_status: ProcessingStatus;
  upload_timestamp: string;
  message: string;
}

export interface MediaListResponse {
  items: MediaItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface MediaFilters {
  mime_type?: string;
  processing_status?: ProcessingStatus;
  uploaded_by?: string;
  has_pii?: boolean;
  from_date?: string;
  to_date?: string;
  search?: string;
}

export interface RedactMetadataResponse {
  id: string;
  redacted_at: string;
  redacted_by: string;
  original_path: string;
  redacted_path: string;
  scrubbed_fields: string[];
}

export interface MediaUploadProgress {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
  mediaId?: string;
}

// Classification types from vision processing
export type MediaClassification =
  | "document"
  | "photograph"
  | "screenshot"
  | "diagram"
  | "surveillance_still"
  | "medical_image"
  | "chart"
  | "mixed"
  | "unknown";

export const MIME_TYPE_MAP: Record<string, MediaType> = {
  "image/jpeg": "image",
  "image/png": "image",
  "image/tiff": "image",
  "image/webp": "image",
  "video/mp4": "video",
  "video/quicktime": "video",
  "video/x-msvideo": "video",
  "application/pdf": "pdf",
};

export const ALLOWED_MIME_TYPES = Object.keys(MIME_TYPE_MAP);
export const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB
