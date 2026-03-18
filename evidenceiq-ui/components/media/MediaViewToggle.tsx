/**
 * MediaViewToggle Component
 * Grid vs Table view toggle.
 */

"use client";

import { Grid3X3, List } from "lucide-react";
import { cn } from "@/lib/utils/cn";

type ViewMode = "grid" | "table";

interface MediaViewToggleProps {
  current: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function MediaViewToggle({ current, onChange }: MediaViewToggleProps) {
  return (
    <div className="flex items-center bg-surface-raised border border-border rounded-md p-1">
      <button
        onClick={() => onChange("grid")}
        className={cn(
          "p-2 rounded transition-colors",
          current === "grid"
            ? "bg-accent text-background"
            : "text-text-secondary hover:text-text-primary"
        )}
        title="Grid view"
      >
        <Grid3X3 className="w-4 h-4" />
      </button>
      <button
        onClick={() => onChange("table")}
        className={cn(
          "p-2 rounded transition-colors",
          current === "table"
            ? "bg-accent text-background"
            : "text-text-secondary hover:text-text-primary"
        )}
        title="Table view"
      >
        <List className="w-4 h-4" />
      </button>
    </div>
  );
}
