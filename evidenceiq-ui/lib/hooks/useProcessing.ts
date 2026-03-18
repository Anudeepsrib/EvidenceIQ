/**
 * useProcessing Hook
 * TanStack Query hooks for processing operations.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { processingApi } from "@/lib/api/processing";

const PROCESSING_QUERY_KEY = "processing";

// Get available models
export function useModels() {
  return useQuery({
    queryKey: [PROCESSING_QUERY_KEY, "models"],
    queryFn: () => processingApi.getModels(),
  });
}

// Process media item
export function useProcessMedia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, model, force }: { id: string; model?: string; force?: boolean }) =>
      processingApi.processMedia(id, model, force),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["media", id] });
      toast.success("Processing started");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Processing failed");
    },
  });
}

// Batch process media items
export function useBatchProcess() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: processingApi.batchProcess,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["media"] });
      toast.success("Batch processing started");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Batch processing failed");
    },
  });
}
