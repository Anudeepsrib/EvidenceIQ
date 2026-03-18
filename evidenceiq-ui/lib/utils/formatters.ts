/**
 * Utility: Formatters
 * Formatting utilities for file sizes, hashes, dates, and technical values.
 */

import { format, formatDistanceToNow, parseISO } from "date-fns";

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log10(bytes) / 3);
  const value = bytes / Math.pow(1024, i);
  return `${value.toFixed(i === 0 ? 0 : 2)} ${units[i]}`;
}

/**
 * Truncate SHA256 hash for display: first 12 + ... + last 6
 */
export function formatHash(hash: string): string {
  if (!hash || hash.length < 20) return hash || "";
  return `${hash.slice(0, 12)}...${hash.slice(-6)}`;
}

/**
 * Format date to readable string
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  return format(d, "MMM d, yyyy HH:mm");
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeDate(date: string | Date): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}

/**
 * Format ISO timestamp for EXIF display (JetBrains Mono style)
 */
export function formatExifTimestamp(date: string | Date): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  return format(d, "yyyy:MM:dd HH:mm:ss");
}

/**
 * Format duration in seconds to readable format
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}m ${secs}s`;
  }
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${mins}m`;
}

/**
 * Format similarity score as percentage
 */
export function formatSimilarity(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

/**
 * Get color class based on similarity score
 */
export function getSimilarityColor(score: number): string {
  if (score >= 0.85) return "text-success";
  if (score >= 0.65) return "text-accent";
  return "text-text-tertiary";
}

/**
 * Get background color class based on similarity score
 */
export function getSimilarityBgColor(score: number): string {
  if (score >= 0.85) return "bg-success/15";
  if (score >= 0.65) return "bg-accent/15";
  return "bg-text-tertiary/15";
}
