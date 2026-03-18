/**
 * Search Types
 * TypeScript interfaces for semantic and tag search.
 */

import type { MediaItem } from "./media";

export interface SemanticSearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
}

export interface TagSearchRequest {
  tags: string[];
  match_type?: "all" | "any";
  limit?: number;
}

export interface CombinedSearchRequest {
  query?: string;
  tags?: string[];
  mime_type?: string;
  sensitivity?: "any" | "flagged" | "clean";
  uploaded_by?: string;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}

export interface SearchResult {
  media: MediaItem;
  similarity_score: number | null;
  matched_tags: string[];
  search_type: "semantic" | "tag" | "combined";
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  search_time_ms: number;
}

export interface SearchSuggestion {
  type: "recent" | "popular" | "tag";
  value: string;
  count?: number;
}

export interface SearchFilters {
  media_types: ("image" | "video" | "pdf" | "frame")[];
  sensitivity: "any" | "flagged" | "clean";
  uploader: string | null;
  date_from: string | null;
  date_to: string | null;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  result_count: number;
}
