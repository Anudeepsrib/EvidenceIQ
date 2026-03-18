/**
 * User Management Page
 * Admin-only user management.
 */

"use client";

import { Users } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

export default function UsersPage() {
  return (
    <div>
      <PageHeader
        title="User Management"
        description="Manage system users and roles"
      />

      <div className="bg-surface border border-border rounded-lg p-8 text-center">
        <Users className="w-12 h-12 text-text-tertiary mx-auto mb-4" />
        <p className="text-text-secondary">
          User management functionality will be implemented here.
        </p>
        <p className="text-text-tertiary text-sm mt-2">
          Create, edit roles, and deactivate users. Roles: admin, investigator, reviewer, viewer.
        </p>
      </div>
    </div>
  );
}
