/**
 * Report Types
 * TypeScript interfaces for evidence reports.
 */

export interface ReportMediaItem {
  media_id: string;
  note: string | null;
}

export interface CreateReportRequest {
  case_name: string;
  case_notes: string | null;
  media_items: ReportMediaItem[];
}

export interface Report {
  id: string;
  case_name: string;
  case_notes: string | null;
  generated_by: string;
  generated_at: string;
  item_count: number;
  file_size_bytes: number | null;
  download_url: string | null;
}

export interface ReportDetail extends Report {
  media_items: ReportMediaItemDetail[];
}

export interface ReportMediaItemDetail {
  media_id: string;
  filename: string;
  mime_type: string;
  sha256_hash: string;
  upload_timestamp: string;
  uploaded_by: string;
  classification: string | null;
  description: string | null;
  tags: string[];
  note: string | null;
  thumbnail_url: string | null;
}

export interface ReportListResponse {
  reports: Report[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReportGenerationProgress {
  report_id: string;
  status: "generating" | "completed" | "failed";
  progress_percent: number;
  current_item: number;
  total_items: number;
  message: string | null;
}
