/**
 * HashDisplay Component
 * Truncated SHA256 hash with copy button - chain of custody signal.
 */

"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface HashDisplayProps {
  hash: string;
  showLabel?: boolean;
}

export function HashDisplay({ hash, showLabel = true }: HashDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(hash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy hash:", err);
    }
  };

  const truncatedHash =
    hash.length > 20 ? `${hash.slice(0, 12)}...${hash.slice(-6)}` : hash;

  return (
    <div className="flex items-center gap-2 font-mono text-xs text-text-secondary">
      {showLabel && <span className="text-text-tertiary">SHA256</span>}
      <span>{truncatedHash}</span>
      <button
        onClick={handleCopy}
        className="p-1 hover:text-accent transition-colors focus:outline-none"
        title="Copy full hash"
      >
        {copied ? (
          <Check className="w-3.5 h-3.5 text-success" />
        ) : (
          <Copy className="w-3.5 h-3.5" />
        )}
      </button>
    </div>
  );
}
