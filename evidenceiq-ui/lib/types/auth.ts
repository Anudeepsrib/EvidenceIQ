/**
 * Authentication Types
 * TypeScript interfaces for auth API responses and JWT token data.
 */

export type Role = "admin" | "investigator" | "reviewer" | "viewer";

export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordChangeResponse {
  message: string;
}

// JWT payload structure (decoded)
export interface JWTPayload {
  sub: string; // user id
  username: string;
  role: Role;
  permissions: string[];
  exp: number;
  iat: number;
  jti: string; // token id
}

// Role permission mapping (matches backend)
export const ROLE_PERMISSIONS = {
  admin: [
    "upload_media",
    "view_search",
    "tag_classify",
    "export_report",
    "redact_metadata",
    "manage_users",
    "delete_media",
    "view_audit_logs",
  ],
  investigator: [
    "upload_media",
    "view_search",
    "tag_classify",
    "export_report",
    "redact_metadata",
    "view_audit_logs",
  ],
  reviewer: ["view_search", "export_report"],
  viewer: ["view_search"],
} as const;

export type Permission =
  | "upload_media"
  | "view_search"
  | "tag_classify"
  | "export_report"
  | "redact_metadata"
  | "manage_users"
  | "delete_media"
  | "view_audit_logs";
