/**
 * useSearch Hook
 * TanStack Query hooks for search operations.
 */

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { searchApi } from "@/lib/api/search";
import { useSearchStore } from "@/lib/stores/searchStore";
import type { CombinedSearchRequest, SearchResponse } from "@/lib/types/search";

export function useSearch() {
  const addToHistory = useSearchStore((state) => state.addToHistory);

  return useMutation({
    mutationFn: async (params: CombinedSearchRequest): Promise<SearchResponse> => {
      const response = await searchApi.combinedSearch(params);
      return response;
    },
    onSuccess: (data, variables) => {
      addToHistory(variables.query || "", data.total);
    },
    onError: (error: Error) => {
      toast.error(error.message || "Search failed");
    },
  });
}
