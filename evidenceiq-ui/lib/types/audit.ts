/**
 * Audit Types
 * TypeScript interfaces for audit log entries.
 */

export type AuditAction =
  | "UPLOAD"
  | "PROCESS"
  | "SEARCH"
  | "REDACT"
  | "REPORT_GENERATE"
  | "LOGIN"
  | "LOGOUT"
  | "USER_CREATE"
  | "USER_UPDATE"
  | "ROLE_CHANGE"
  | "DELETE"
  | "VIEW"
  | "EXPORT";

export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  username: string | null;
  user_role: string | null;
  action: AuditAction;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  user_agent: string | null;
  status: "success" | "failure" | "blocked";
  timestamp: string;
}

export interface AuditLogListResponse {
  entries: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogFilters {
  user_id?: string;
  action?: AuditAction;
  resource_type?: string;
  status?: "success" | "failure" | "blocked";
  from_date?: string;
  to_date?: string;
}

// Color mapping for audit action badges
export const AUDIT_ACTION_COLORS: Record<AuditAction, string> = {
  UPLOAD: "blue",
  PROCESS: "purple",
  SEARCH: "teal",
  REDACT: "amber",
  REPORT_GENERATE: "green",
  LOGIN: "gray",
  LOGOUT: "gray",
  USER_CREATE: "lime",
  USER_UPDATE: "orange",
  ROLE_CHANGE: "orange",
  DELETE: "red",
  VIEW: "cyan",
  EXPORT: "pink",
};
