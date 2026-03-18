/**
 * FullPageSpinner Component
 * Centered loading spinner for page transitions.
 */

import { Loader2 } from "lucide-react";

interface FullPageSpinnerProps {
  message?: string;
}

export function FullPageSpinner({ message = "Loading..." }: FullPageSpinnerProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-8 h-8 text-accent animate-spin" />
      <p className="text-text-secondary text-sm">{message}</p>
    </div>
  );
}
