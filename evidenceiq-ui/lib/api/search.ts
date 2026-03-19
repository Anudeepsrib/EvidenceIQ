/**
 * Search API
 * API calls for semantic and tag search.
 */

import apiClient from "./client";
import type {
  SemanticSearchRequest,
  TagSearchRequest,
  CombinedSearchRequest,
  SearchResponse,
} from "@/lib/types/search";

export const searchApi = {
  // Semantic search
  semanticSearch: async (params: SemanticSearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>("/search/semantic", params);
    return response.data;
  },

  // Tag search
  tagSearch: async (params: TagSearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>("/search/tags", params);
    return response.data;
  },

  // Combined search
  combinedSearch: async (params: CombinedSearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>("/search/combined", params);
    return response.data;
  },
};

export default searchApi;
