/**
 * Media API
 * API calls for media management.
 */

import apiClient from "./client";
import type {
  MediaUploadResponse,
  MediaItem,
  MediaListResponse,
  MediaFilters,
  RedactMetadataResponse,
} from "@/lib/types/media";

export const mediaApi = {
  // Get media list with pagination and filters
  getMedia: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: MediaFilters
  ): Promise<MediaListResponse> => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    
    if (filters?.mime_type) params.set("mime_type", filters.mime_type);
    if (filters?.processing_status) params.set("processing_status", filters.processing_status);
    if (filters?.uploaded_by) params.set("uploaded_by", filters.uploaded_by);
    if (filters?.has_pii !== undefined) params.set("has_pii", String(filters.has_pii));
    if (filters?.from_date) params.set("from_date", filters.from_date);
    if (filters?.to_date) params.set("to_date", filters.to_date);
    if (filters?.search) params.set("search", filters.search);
    
    const response = await apiClient.get<MediaListResponse>(`/media?${params.toString()}`);
    return response.data;
  },

  // Get single media item
  getMediaItem: async (id: string): Promise<MediaItem> => {
    const response = await apiClient.get<MediaItem>(`/media/${id}`);
    return response.data;
  },

  // Upload media file
  uploadMedia: async (file: File, onProgress?: (progress: number) => void): Promise<MediaUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await apiClient.post<MediaUploadResponse>("/media/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return response.data;
  },

  // Delete media item
  deleteMedia: async (id: string): Promise<void> => {
    await apiClient.delete(`/media/${id}`);
  },

  // Redact metadata
  redactMetadata: async (id: string): Promise<RedactMetadataResponse> => {
    const response = await apiClient.post<RedactMetadataResponse>(`/media/${id}/redact`);
    return response.data;
  },

  // Get media file URL
  getMediaFileUrl: (id: string, redacted: boolean = false): string => {
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${base}/media/${id}/file${redacted ? "?use_redacted=true" : ""}`;
  },
};

export default mediaApi;
