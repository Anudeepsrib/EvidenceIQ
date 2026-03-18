/**
 * PIIFlagBanner Component
 * Amber warning banner for PII detected in EXIF.
 */

import { AlertTriangle } from "lucide-react";

interface PIIFlagBannerProps {
  piiFlags: Record<string, unknown> | null;
}

export function PIIFlagBanner({ piiFlags }: PIIFlagBannerProps) {
  if (!piiFlags || Object.keys(piiFlags).length === 0) {
    return null;
  }

  const flagList = Object.keys(piiFlags);

  return (
    <div className="w-full bg-flag-pii/10 border border-flag-pii/30 rounded-md p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-flag-pii flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-flag-pii font-medium">
            PII detected in EXIF metadata
          </p>
          <p className="text-flag-pii/80 text-sm mt-1">
            Fields: {flagList.join(", ")}
          </p>
          <p className="text-text-secondary text-xs mt-1">
            Redact to remove sensitive location and device information.
          </p>
        </div>
      </div>
    </div>
  );
}
