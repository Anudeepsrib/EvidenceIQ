/**
 * RoleGuard Component
 * Hides children if user doesn't have required role/permission.
 */

"use client";

import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";
import type { Role } from "@/lib/types/auth";

type PermissionKey = keyof typeof permissions;

interface RoleGuardProps {
  children: React.ReactNode;
  requiredRole?: Role;
  requiredPermission?: PermissionKey;
  fallback?: React.ReactNode;
}

export function RoleGuard({
  children,
  requiredRole,
  requiredPermission,
  fallback = null,
}: RoleGuardProps) {
  const user = useAuthStore((state) => state.user);

  if (!user) return <>{fallback}</>;

  // Check role requirement
  if (requiredRole && user.role !== requiredRole) {
    return <>{fallback}</>;
  }

  // Check permission requirement
  if (requiredPermission) {
    const hasPermission = permissions[requiredPermission](user.role);
    if (!hasPermission) {
      return <>{fallback}</>;
    }
  }

  return <>{children}</>;
}
