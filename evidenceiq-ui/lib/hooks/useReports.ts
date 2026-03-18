/**
 * useReports Hook
 * TanStack Query hooks for reports.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { reportsApi } from "@/lib/api/reports";
import type { CreateReportRequest } from "@/lib/types/report";

const REPORTS_QUERY_KEY = "reports";

// Get reports list
export function useReports(page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, "list", page, pageSize],
    queryFn: () => reportsApi.getReports(page, pageSize),
  });
}

// Get single report
export function useReport(id: string | null) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, id],
    queryFn: () => reportsApi.getReport(id!),
    enabled: !!id,
  });
}

// Create report
export function useCreateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: reportsApi.createReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REPORTS_QUERY_KEY, "list"] });
      toast.success("Report created successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to create report");
    },
  });
}

// Download report
export function useDownloadReport() {
  return useMutation({
    mutationFn: async (id: string) => {
      const blob = await reportsApi.downloadReport(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `report-${id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    onSuccess: () => {
      toast.success("Report downloaded");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Download failed");
    },
  });
}
