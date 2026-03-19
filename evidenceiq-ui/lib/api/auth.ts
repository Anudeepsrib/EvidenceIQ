/**
 * Auth API
 * Authentication API calls for EvidenceIQ backend.
 */

import apiClient from "./client";
import type {
  LoginRequest,
  LoginResponse,
  RefreshRequest,
  PasswordChangeRequest,
  PasswordChangeResponse,
  UserResponse,
} from "@/lib/types/auth";

export const api = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>("/auth/login", data);
    return response.data;
  },

  refresh: async (data: RefreshRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>("/auth/refresh", data);
    return response.data;
  },

  me: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>("/auth/me");
    return response.data;
  },

  changePassword: async (
    data: PasswordChangeRequest
  ): Promise<PasswordChangeResponse> => {
    const response = await apiClient.post<PasswordChangeResponse>(
      "/auth/change-password",
      data
    );
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
  },
};

export default api;
