/**
 * ExifMetadataPanel Component
 * Display scrubbed EXIF metadata.
 */

import { Lock } from "lucide-react";
import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";

interface ExifMetadataPanelProps {
  exifData: Record<string, unknown> | null;
  isRedacted: boolean;
}

export function ExifMetadataPanel({ exifData, isRedacted }: ExifMetadataPanelProps) {
  const user = useAuthStore((state) => state.user);
  const canViewExif = user ? permissions.canViewExif(user.role) : false;

  if (!canViewExif) {
    return (
      <div className="bg-surface border border-border rounded-lg p-4">
        <div className="flex items-center gap-2 text-text-secondary">
          <Lock className="w-4 h-4" />
          <span>EXIF access restricted</span>
        </div>
      </div>
    );
  }

  if (!exifData || Object.keys(exifData).length === 0) {
    return (
      <div className="bg-surface border border-border rounded-lg p-4">
        <p className="text-text-secondary text-sm">No EXIF data available</p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-text-primary">EXIF Metadata</h3>
        {isRedacted && (
          <div className="flex items-center gap-1 text-accent text-sm">
            <Lock className="w-3 h-3" />
            <span>Redacted</span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        {Object.entries(exifData).map(([key, value]) => (
          <div key={key} className="flex justify-between items-start gap-4 py-1 border-b border-border/50 last:border-0">
            <span className="text-text-secondary text-sm">{key}</span>
            <span className="font-mono text-sm text-text-primary text-right break-all">
              {value === "REDACTED" ? (
                <span className="text-accent">REDACTED</span>
              ) : value === "[Flagged — redact to remove]" ? (
                <span className="text-flag-pii">{String(value)}</span>
              ) : (
                String(value)
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
