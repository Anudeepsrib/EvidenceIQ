/**
 * MediaGrid Component
 * Grid view of media cards.
 */

import { MediaCard } from "./MediaCard";
import type { MediaItem } from "@/lib/types/media";

interface MediaGridProps {
  media: MediaItem[];
  selectedIds?: Set<string>;
}

export function MediaGrid({ media, selectedIds }: MediaGridProps) {
  if (media.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {media.map((item) => (
        <MediaCard
          key={item.id}
          media={item}
          isSelected={selectedIds?.has(item.id)}
        />
      ))}
    </div>
  );
}
