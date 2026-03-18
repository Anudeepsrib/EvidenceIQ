/**
 * Processing Types
 * TypeScript interfaces for vision processing results.
 */

export interface VisionTags {
  people_present: boolean;
  estimated_people_count: number | null;
  faces_visible: boolean;
  text_visible: boolean;
  location_type: "indoor" | "outdoor" | "unknown";
  time_of_day: "day" | "night" | "unknown";
  objects: string[];
  scene_tags: string[];
  sensitive_content_flags: string[];
}

export interface VisionClassification {
  document_type: string;
  confidence: "high" | "medium" | "low";
  explanation: string;
}

export interface VisionDescription {
  description: string;
  language: string;
  length_chars: number;
}

export interface VisionResults {
  model_used: string;
  steps_completed: string[];
  steps_failed: string[];
  classification: string;
  description: string;
  tags: VisionTags;
  success: boolean;
}

export interface ProcessingResult {
  id: string;
  media_id: string;
  model_used: string;
  classification: string | null;
  description: string | null;
  tags: VisionTags | null;
  processed_at: string;
  processing_time_ms: number | null;
  success: boolean;
  error_message: string | null;
}

export interface ProcessingStatusResponse {
  media_id: string;
  status: "pending" | "processing" | "ready" | "failed";
  progress_percent: number | null;
  current_step: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface BatchProcessingRequest {
  media_ids: string[];
  model?: string;
  force?: boolean;
}

export interface BatchProcessingResponse {
  job_id: string;
  submitted: number;
  message: string;
}

export interface AvailableModel {
  name: string;
  description: string;
  available: boolean;
}

export interface ModelsListResponse {
  models: AvailableModel[];
  default: string;
}
