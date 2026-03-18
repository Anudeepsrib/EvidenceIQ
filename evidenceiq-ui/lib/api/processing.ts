/**
 * Processing API
 * API calls for media processing.
 */

import apiClient from "../client";
import type {
  ProcessingResult,
  ProcessingStatusResponse,
  BatchProcessingRequest,
  BatchProcessingResponse,
  ModelsListResponse,
} from "@/lib/types/processing";

export const processingApi = {
  // Process single media item
  processMedia: async (id: string, model?: string, force?: boolean): Promise<ProcessingResult> => {
    const params = new URLSearchParams();
    if (model) params.set("model", model);
    if (force) params.set("force", "true");
    
    const response = await apiClient.post<ProcessingResult>(
      `/processing/${id}?${params.toString()}`
    );
    return response.data;
  },

  // Batch process multiple items
  batchProcess: async (data: BatchProcessingRequest): Promise<BatchProcessingResponse> => {
    const response = await apiClient.post<BatchProcessingResponse>("/processing/batch", data);
    return response.data;
  },

  // Get processing status
  getProcessingStatus: async (id: string): Promise<ProcessingStatusResponse> => {
    const response = await apiClient.get<ProcessingStatusResponse>(`/processing/${id}/status`);
    return response.data;
  },

  // Get available models
  getModels: async (): Promise<ModelsListResponse> => {
    const response = await apiClient.get<ModelsListResponse>("/processing/models");
    return response.data;
  },
};

export default processingApi;
