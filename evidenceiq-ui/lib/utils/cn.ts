/**
 * Utility: Class Name Merge
 * Merges Tailwind classes with proper precedence handling.
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
