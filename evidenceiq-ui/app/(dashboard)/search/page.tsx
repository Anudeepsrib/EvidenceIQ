/**
 * Search Page
 * Semantic + tag search interface.
 */

"use client";

import { useState } from "react";
import { Search, Clock, Filter } from "lucide-react";
import Link from "next/link";

import { useSearch } from "@/lib/hooks/useSearch";
import { useSearchStore } from "@/lib/stores/searchStore";
import { cn } from "@/lib/utils/cn";
import { formatSimilarity, getSimilarityColor, getSimilarityBgColor } from "@/lib/utils/formatters";

import { PageHeader } from "@/components/layout/PageHeader";
import { FullPageSpinner } from "@/components/ui/FullPageSpinner";
import { MediaTypeBadge } from "@/components/media/MediaTypeBadge";
import { detectMediaType } from "@/lib/utils/mediaUtils";
import { mediaApi } from "@/lib/api/media";
import type { SearchResult } from "@/lib/types/search";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const searchMutation = useSearch();
  const { history, filters, setFilters, toggleMediaType, clearFilters } = useSearchStore();

  const handleSearch = async () => {
    if (!query.trim()) return;

    const response = await searchMutation.mutateAsync({
      query: query.trim(),
      limit: 20,
      ...filters,
    });

    setResults(response.results);
    setHasSearched(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const replaySearch = (queryText: string) => {
    setQuery(queryText);
    searchMutation.mutateAsync({
      query: queryText,
      limit: 20,
    }).then((response) => {
      setResults(response.results);
      setHasSearched(true);
    });
  };

  return (
    <div>
      <PageHeader
        title="Search"
        description="Find media using natural language or tags"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main search area - 65% */}
        <div className="lg:col-span-2 space-y-6">
          {/* Search input */}
          <div className="bg-surface border border-border rounded-lg p-4">
            <div className="flex gap-3">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you're looking for — e.g. 'outdoor photos with people at night'"
                className="flex-1 bg-surface-raised border border-border rounded-md px-4 py-3 text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent resize-none h-24"
              />
            </div>
            <div className="flex items-center justify-between mt-3">
              <span className="text-xs text-text-tertiary">
                Model: llava 7B (local)
              </span>
              <button
                onClick={handleSearch}
                disabled={!query.trim() || searchMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-background font-medium rounded-md transition-colors disabled:opacity-50"
              >
                {searchMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    Search
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results */}
          {searchMutation.isPending && (
            <div className="flex items-center justify-center py-20">
              <FullPageSpinner message="Searching..." />
            </div>
          )}

          {hasSearched && !searchMutation.isPending && results.length === 0 && (
            <div className="text-center py-20">
              <p className="text-text-secondary">
                No results found. Try describing the scene differently.
              </p>
            </div>
          )}

          {results.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {results.map((result) => (
                <SearchResultCard key={result.media.id} result={result} />
              ))}
            </div>
          )}
        </div>

        {/* Filters + History - 35% */}
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-surface border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-4 h-4 text-text-secondary" />
              <h3 className="font-medium text-text-primary">Filters</h3>
            </div>

            {/* Media type */}
            <div className="mb-4">
              <p className="text-text-tertiary text-xs uppercase mb-2">Media Type</p>
              <div className="space-y-2">
                {["image", "video", "pdf"].map((type) => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.media_types.includes(type as any)}
                      onChange={() => toggleMediaType(type as any)}
                      className="rounded border-border bg-surface-raised text-accent focus:ring-accent"
                    />
                    <span className="text-sm text-text-secondary capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Sensitivity */}
            <div className="mb-4">
              <p className="text-text-tertiary text-xs uppercase mb-2">Sensitivity</p>
              <select
                value={filters.sensitivity}
                onChange={(e) => setFilters({ sensitivity: e.target.value as any })}
                className="w-full bg-surface-raised border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <option value="any">Any</option>
                <option value="flagged">Flagged only</option>
                <option value="clean">Clean only</option>
              </select>
            </div>

            <button
              onClick={clearFilters}
              className="text-sm text-accent hover:underline"
            >
              Clear filters
            </button>
          </div>

          {/* History */}
          {history.length > 0 && (
            <div className="bg-surface border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-4 h-4 text-text-secondary" />
                <h3 className="font-medium text-text-primary">Recent Searches</h3>
              </div>
              <div className="space-y-2">
                {history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => replaySearch(item.query)}
                    className="w-full text-left p-2 hover:bg-surface-raised rounded transition-colors"
                  >
                    <p className="text-sm text-text-primary truncate">{item.query}</p>
                    <p className="text-xs text-text-tertiary">
                      {item.result_count} results
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Search result card component
function SearchResultCard({ result }: { result: SearchResult }) {
  const mediaType = detectMediaType(result.media.mime_type);
  const score = result.similarity_score || 0;

  return (
    <Link
      href={`/media/${result.media.id}`}
      className="bg-surface border border-border rounded-lg overflow-hidden hover:border-border-strong transition-colors"
    >
      {/* Thumbnail */}
      <div className="aspect-video bg-surface-raised relative">
        <img
          src={mediaApi.getMediaFileUrl(result.media.id)}
          alt={result.media.original_filename}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Info */}
      <div className="p-3">
        {/* Similarity bar */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-text-tertiary">Similarity</span>
            <span className={cn("text-xs font-medium", getSimilarityColor(score))}>
              {formatSimilarity(score)}
            </span>
          </div>
          <div className="h-1.5 bg-surface-raised rounded-full overflow-hidden">
            <div
              className={cn("h-full rounded-full", getSimilarityBgColor(score).replace("/15", ""))}
              style={{ width: `${score * 100}%` }}
            />
          </div>
        </div>

        <h4 className="text-sm font-medium text-text-primary truncate">
          {result.media.original_filename}
        </h4>

        <div className="flex items-center gap-2 mt-2">
          <MediaTypeBadge type={mediaType} size="sm" />
        </div>
      </div>
    </Link>
  );
}
