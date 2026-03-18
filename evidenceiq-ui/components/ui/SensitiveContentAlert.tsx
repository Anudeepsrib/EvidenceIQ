/**
 * SensitiveContentAlert Component
 * Non-dismissible red alert for sensitive content - always above the fold.
 */

import { AlertTriangle } from "lucide-react";

interface SensitiveContentAlertProps {
  flags: string[];
}

export function SensitiveContentAlert({ flags }: SensitiveContentAlertProps) {
  // Don't render if only "none" or empty
  const displayFlags = flags.filter((f) => f !== "none");
  if (displayFlags.length === 0) return null;

  const flagText = displayFlags.join(", ");

  return (
    <div className="w-full bg-error/10 border border-error/30 rounded-md p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-error font-medium">
            Sensitive content detected: {flagText}
          </p>
          <p className="text-error/80 text-sm mt-1">
            Access to this item has been logged.
          </p>
        </div>
      </div>
    </div>
  );
}
