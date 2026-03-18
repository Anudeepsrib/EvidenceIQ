/**
 * RedactMetadataButton Component
 * Button to trigger metadata redaction.
 */

"use client";

import { useState } from "react";
import { Shield, AlertCircle } from "lucide-react";
import { toast } from "sonner";

import { useRedactMetadata } from "@/lib/hooks/useMedia";
import { useAuthStore } from "@/lib/stores/authStore";
import { permissions } from "@/lib/utils/permissions";

interface RedactMetadataButtonProps {
  mediaId: string;
}

export function RedactMetadataButton({ mediaId }: RedactMetadataButtonProps) {
  const user = useAuthStore((state) => state.user);
  const canRedact = user ? permissions.canRedactMetadata(user.role) : false;
  const [showConfirm, setShowConfirm] = useState(false);
  const redactMutation = useRedactMetadata();

  if (!canRedact) return null;

  const handleRedact = async () => {
    try {
      await redactMutation.mutateAsync(mediaId);
      setShowConfirm(false);
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <>
      <button
        onClick={() => setShowConfirm(true)}
        disabled={redactMutation.isPending}
        className="flex items-center gap-2 px-4 py-2 bg-surface-raised hover:bg-surface border border-border text-text-primary rounded-md transition-colors disabled:opacity-50"
      >
        <Shield className="w-4 h-4" />
        <span>Redact Metadata</span>
      </button>

      {/* Confirmation Dialog */}
      {showConfirm && (
        <div className="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
          <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-start gap-3 mb-4">
              <AlertCircle className="w-5 h-5 text-accent mt-0.5" />
              <div>
                <h3 className="font-medium text-text-primary">Confirm Redaction</h3>
                <p className="text-text-secondary text-sm mt-1">
                  This will permanently scrub GPS, serial number, and owner fields from EXIF.
                  A redacted copy will be created.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 text-text-secondary hover:text-text-primary transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleRedact}
                disabled={redactMutation.isPending}
                className="px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded-md transition-colors disabled:opacity-50"
              >
                {redactMutation.isPending ? "Redacting..." : "Continue"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
