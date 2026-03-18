/**
 * Search Store
 * Zustand store for search history and filters.
 */

import { create } from "zustand";
import type { SearchHistoryItem, SearchFilters } from "@/lib/types/search";

interface SearchState {
  // Session search history
  history: SearchHistoryItem[];
  
  // Current search filters
  filters: SearchFilters;
  
  // Actions
  addToHistory: (query: string, resultCount: number) => void;
  clearHistory: () => void;
  removeHistoryItem: (id: string) => void;
  
  setFilters: (filters: Partial<SearchFilters>) => void;
  clearFilters: () => void;
  
  // Toggle filter helpers
  toggleMediaType: (type: "image" | "video" | "pdf" | "frame") => void;
  setSensitivity: (value: SearchFilters["sensitivity"]) => void;
}

const MAX_HISTORY_ITEMS = 8;

export const useSearchStore = create<SearchState>()((set, get) => ({
  history: [],
  filters: {
    media_types: [],
    sensitivity: "any",
    uploader: null,
    date_from: null,
    date_to: null,
  },
  
  addToHistory: (query, resultCount) => {
    const newItem: SearchHistoryItem = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      query,
      timestamp: new Date().toISOString(),
      result_count: resultCount,
    };
    
    set((state) => ({
      history: [newItem, ...state.history].slice(0, MAX_HISTORY_ITEMS),
    }));
  },
  
  clearHistory: () => set({ history: [] }),
  
  removeHistoryItem: (id) =>
    set((state) => ({
      history: state.history.filter((item) => item.id !== id),
    })),
  
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  
  clearFilters: () =>
    set({
      filters: {
        media_types: [],
        sensitivity: "any",
        uploader: null,
        date_from: null,
        date_to: null,
      },
    }),
  
  toggleMediaType: (type) =>
    set((state) => {
      const types = state.filters.media_types;
      const newTypes = types.includes(type)
        ? types.filter((t) => t !== type)
        : [...types, type];
      return { filters: { ...state.filters, media_types: newTypes } };
    }),
  
  setSensitivity: (value) =>
    set((state) => ({
      filters: { ...state.filters, sensitivity: value },
    })),
}));
