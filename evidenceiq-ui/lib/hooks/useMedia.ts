/**
 * useMedia Hook
 * TanStack Query hook for media with polling for processing status.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { mediaApi } from "@/lib/api/media";
import type { MediaItem, MediaFilters } from "@/lib/types/media";

const MEDIA_QUERY_KEY = "media";

// Get media list
export function useMedia(
  page: number = 1,
  pageSize: number = 20,
  filters?: MediaFilters
) {
  return useQuery({
    queryKey: [MEDIA_QUERY_KEY, "list", page, pageSize, filters],
    queryFn: () => mediaApi.getMedia(page, pageSize, filters),
  });
}

// Get single media item with polling for processing status
export function useMediaItem(id: string | null) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: [MEDIA_QUERY_KEY, id],
    queryFn: () => mediaApi.getMediaItem(id!),
    enabled: !!id,
    refetchInterval: (query: any) => {
      const data = query?.state?.data;
      // Poll every 5 seconds while processing or pending
      if (data && (data.processing_status === "processing" || data.processing_status === "pending")) {
        return 5000;
      }
      // Stop polling when ready or failed
      return false;
    },
  });
}

// Upload media mutation
export function useUploadMedia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      mediaApi.uploadMedia(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MEDIA_QUERY_KEY, "list"] });
      toast.success("Media uploaded successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Upload failed");
    },
  });
}

// Delete media mutation
export function useDeleteMedia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: mediaApi.deleteMedia,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MEDIA_QUERY_KEY, "list"] });
      toast.success("Media deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Delete failed");
    },
  });
}

// Redact metadata mutation
export function useRedactMetadata() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: mediaApi.redactMetadata,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [MEDIA_QUERY_KEY, id] });
      toast.success("Metadata redacted successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Redaction failed");
    },
  });
}
