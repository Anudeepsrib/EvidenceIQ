/**
 * Reports API
 * API calls for report generation and management.
 */

import apiClient from "../client";
import type {
  CreateReportRequest,
  Report,
  ReportDetail,
  ReportListResponse,
} from "@/lib/types/report";

export const reportsApi = {
  // Create new report
  createReport: async (data: CreateReportRequest): Promise<Report> => {
    const response = await apiClient.post<Report>("/reports/generate", data);
    return response.data;
  },

  // Get all reports
  getReports: async (page: number = 1, pageSize: number = 20): Promise<ReportListResponse> => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    
    const response = await apiClient.get<ReportListResponse>(`/reports?${params.toString()}`);
    return response.data;
  },

  // Get single report
  getReport: async (id: string): Promise<ReportDetail> => {
    const response = await apiClient.get<ReportDetail>(`/reports/${id}`);
    return response.data;
  },

  // Download report PDF
  downloadReport: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/reports/${id}/download`, {
      responseType: "blob",
    });
    return response.data;
  },
};

export default reportsApi;
