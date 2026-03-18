/**
 * Utility: RBAC Permissions
 * Role-based access control permission checks.
 */

import type { Role } from "@/lib/types/auth";

export const permissions = {
  canUpload: (role: Role) => ["admin", "investigator"].includes(role),
  
  canViewMedia: (role: Role) =>
    ["admin", "investigator", "reviewer", "viewer"].includes(role),
  
  canViewExif: (role: Role) => ["admin", "investigator"].includes(role),
  
  canRedactMetadata: (role: Role) => ["admin", "investigator"].includes(role),
  
  canReprocess: (role: Role) => role === "admin",
  
  canDelete: (role: Role) => role === "admin",
  
  canCreateReport: (role: Role) =>
    ["admin", "investigator", "reviewer"].includes(role),
  
  canViewReports: (role: Role) =>
    ["admin", "investigator", "reviewer"].includes(role),
  
  canSearch: (role: Role) =>
    ["admin", "investigator", "reviewer", "viewer"].includes(role),
  
  canViewAuditLog: (role: Role) => role === "admin",
  
  canManageUsers: (role: Role) => role === "admin",
  
  canExportAuditCSV: (role: Role) => role === "admin",
};

// Navigation item visibility
export const navigationItems = [
  { label: "Media Library", href: "/media", requiredPermission: "canViewMedia" },
  { label: "Search", href: "/search", requiredPermission: "canSearch" },
  { label: "Reports", href: "/reports", requiredPermission: "canViewReports" },
  { label: "Audit Log", href: "/audit", requiredPermission: "canViewAuditLog" },
  { label: "Users", href: "/settings/users", requiredPermission: "canManageUsers" },
  { label: "Settings", href: "/settings", requiredPermission: "canViewMedia" },
] as const;

export type NavigationItem = typeof navigationItems[number];
