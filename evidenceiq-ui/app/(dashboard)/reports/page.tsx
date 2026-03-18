/**
 * Reports Page
 * Report list with creation dialog.
 */

"use client";

import { useState } from "react";
import { Plus, Download, Eye, FileText } from "lucide-react";
import Link from "next/link";

import { useReports, useCreateReport, useDownloadReport } from "@/lib/hooks/useReports";
import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";
import { formatDate } from "@/lib/utils/formatters";

import { PageHeader } from "@/components/layout/PageHeader";
import { FullPageSpinner } from "@/components/ui/FullPageSpinner";

export default function ReportsPage() {
  const user = useAuthStore((state) => state.user);
  const canCreateReport = user ? permissions.canCreateReport(user.role) : false;

  const { data, isLoading } = useReports();
  const createMutation = useCreateReport();
  const downloadMutation = useDownloadReport();

  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [caseName, setCaseName] = useState("");
  const [caseNotes, setCaseNotes] = useState("");

  if (isLoading) {
    return <FullPageSpinner message="Loading reports..." />;
  }

  const reports = data?.reports || [];

  const handleCreate = async () => {
    if (!caseName.trim()) return;

    await createMutation.mutateAsync({
      case_name: caseName,
      case_notes: caseNotes || null,
      media_items: [], // Would be populated with selected items
    });

    setShowCreateDialog(false);
    setCaseName("");
    setCaseNotes("");
  };

  return (
    <div>
      <PageHeader title="Evidence Reports" description={`${reports.length} reports`}>
        {canCreateReport && (
          <button
            onClick={() => setShowCreateDialog(true)}
            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded-md transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Report
          </button>
        )}
      </PageHeader>

      {/* Reports list */}
      {reports.length === 0 ? (
        <div className="text-center py-20">
          <FileText className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
          <p className="text-text-secondary">No reports yet</p>
          {canCreateReport && (
            <button
              onClick={() => setShowCreateDialog(true)}
              className="mt-4 text-accent hover:underline"
            >
              Create your first report
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-surface border border-border rounded-lg p-4 hover:border-border-strong transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-heading italic text-lg text-text-primary">
                    {report.case_name}
                  </h3>
                  <p className="text-text-secondary text-sm mt-1">
                    {formatDate(report.generated_at)}
                  </p>
                </div>
                <div className="bg-accent-muted text-accent text-xs font-medium px-2 py-1 rounded">
                  {report.item_count} items
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <Link
                  href={`/reports/${report.id}`}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-surface-raised hover:bg-surface border border-border rounded transition-colors text-sm"
                >
                  <Eye className="w-4 h-4" />
                  Preview
                </Link>
                <button
                  onClick={() => downloadMutation.mutate(report.id)}
                  disabled={downloadMutation.isPending}
                  className="flex items-center justify-center gap-2 px-3 py-2 bg-accent hover:bg-accent-hover text-background rounded transition-colors text-sm disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Report Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
          <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="font-medium text-text-primary mb-4">Create New Report</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Case Name *
                </label>
                <input
                  type="text"
                  value={caseName}
                  onChange={(e) => setCaseName(e.target.value)}
                  placeholder="e.g., Investigation #2024-001"
                  className="w-full bg-surface-raised border border-border rounded px-3 py-2 text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Case Notes
                </label>
                <textarea
                  value={caseNotes}
                  onChange={(e) => setCaseNotes(e.target.value)}
                  placeholder="Optional notes about this case..."
                  className="w-full bg-surface-raised border border-border rounded px-3 py-2 text-text-primary focus:outline-none focus:ring-2 focus:ring-accent h-24 resize-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateDialog(false)}
                className="px-4 py-2 text-text-secondary hover:text-text-primary transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!caseName.trim() || createMutation.isPending}
                className="px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? "Creating..." : "Create Report"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
