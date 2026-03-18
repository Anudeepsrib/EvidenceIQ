/**
 * Media Store
 * Zustand store for media library state.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { MediaItem, MediaFilters } from "@/lib/types/media";

type ViewMode = "grid" | "table";

interface MediaState {
  // View state
  viewMode: ViewMode;
  selectedItems: Set<string>;
  filters: MediaFilters;
  
  // Upload state
  isUploadPanelOpen: boolean;
  
  // Actions
  setViewMode: (mode: ViewMode) => void;
  toggleSelectedItem: (id: string) => void;
  clearSelectedItems: () => void;
  selectAllItems: (ids: string[]) => void;
  setFilters: (filters: Partial<MediaFilters>) => void;
  clearFilters: () => void;
  setUploadPanelOpen: (open: boolean) => void;
  
  // Computed helpers
  isSelected: (id: string) => boolean;
}

export const useMediaStore = create<MediaState>()(
  persist(
    (set, get) => ({
      viewMode: "grid",
      selectedItems: new Set(),
      filters: {},
      isUploadPanelOpen: false,
      
      setViewMode: (mode) => set({ viewMode: mode }),
      
      toggleSelectedItem: (id) =>
        set((state) => {
          const newSelected = new Set(state.selectedItems);
          if (newSelected.has(id)) {
            newSelected.delete(id);
          } else {
            newSelected.add(id);
          }
          return { selectedItems: newSelected };
        }),
      
      clearSelectedItems: () => set({ selectedItems: new Set() }),
      
      selectAllItems: (ids) =>
        set({ selectedItems: new Set(ids) }),
      
      setFilters: (newFilters) =>
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        })),
      
      clearFilters: () => set({ filters: {} }),
      
      setUploadPanelOpen: (open) => set({ isUploadPanelOpen: open }),
      
      isSelected: (id) => get().selectedItems.has(id),
    }),
    {
      name: "media-storage",
      partialize: (state) => ({ viewMode: state.viewMode }),
    }
  )
);
