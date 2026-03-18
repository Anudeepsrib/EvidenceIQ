/**
 * Audit Log Page
 * Admin-only audit log view.
 */

"use client";

import { Shield } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

export default function AuditPage() {
  return (
    <div>
      <PageHeader
        title="Audit Log"
        description="System activity and access logs"
      />

      <div className="bg-surface border border-border rounded-lg p-8 text-center">
        <Shield className="w-12 h-12 text-text-tertiary mx-auto mb-4" />
        <p className="text-text-secondary">
          Audit log functionality will be implemented here.
        </p>
        <p className="text-text-tertiary text-sm mt-2">
          Shows UPLOAD, PROCESS, SEARCH, REDACT, REPORT_GENERATE, LOGIN events.
        </p>
      </div>
    </div>
  );
}
