"use client";

import { useState, useMemo, useCallback } from "react";
import { Search, X, Clock, TrendingUp, Package, AlertCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";

interface SearchResult {
  id: string;
  title: string;
  type: "alert" | "supplier" | "recommendation" | "report";
  description?: string;
  url: string;
  tags?: string[];
}

const mockSearchData: SearchResult[] = [
  {
    id: "1",
    title: "Critical Supply Chain Disruption - Asia Pacific",
    type: "alert",
    description: "Major shipping delays detected in Singapore port",
    url: "/dashboard/alerts/1",
    tags: ["critical", "logistics"],
  },
  {
    id: "2",
    title: "Supplier Risk: ABC Manufacturing",
    type: "supplier",
    description: "Financial risk score increased to 8.5/10",
    url: "/dashboard/suppliers/abc-manufacturing",
    tags: ["high-risk", "manufacturing"],
  },
  {
    id: "3",
    title: "Diversification Strategy for Electronics",
    type: "recommendation",
    description: "Recommended: Add 2 new suppliers in Vietnam",
    url: "/dashboard/recommendations/3",
    tags: ["strategy", "electronics"],
  },
  {
    id: "4",
    title: "Q4 2025 Supply Chain Health Report",
    type: "report",
    description: "Comprehensive analysis of supply chain performance",
    url: "/dashboard/monitoring/reports/q4-2025",
    tags: ["report", "analytics"],
  },
  {
    id: "5",
    title: "XYZ Logistics - Performance Review",
    type: "supplier",
    description: "On-time delivery rate: 94.2%",
    url: "/dashboard/suppliers/xyz-logistics",
    tags: ["logistics", "performance"],
  },
];

const getResultIcon = (type: SearchResult["type"]) => {
  switch (type) {
    case "alert":
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    case "supplier":
      return <Package className="h-4 w-4 text-blue-500" />;
    case "recommendation":
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    case "report":
      return <Clock className="h-4 w-4 text-purple-500" />;
  }
};

const getResultTypeLabel = (type: SearchResult["type"]) => {
  const labels = {
    alert: "Alert",
    supplier: "Supplier",
    recommendation: "Recommendation",
    report: "Report",
  };
  return labels[type];
};

export function SearchBar() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [recentSearches, setRecentSearches] = useState<string[]>([
    "supply chain disruption",
    "high risk suppliers",
    "logistics performance",
  ]);

  // Debounced search function
  const filteredResults = useMemo(() => {
    if (!searchQuery || searchQuery.length < 2) return [];

    const query = searchQuery.toLowerCase();
    return mockSearchData.filter(
      (item) =>
        item.title.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query) ||
        item.tags?.some((tag) => tag.toLowerCase().includes(query))
    );
  }, [searchQuery]);

  const groupedResults = useMemo(() => {
    const groups: Record<string, SearchResult[]> = {
      alert: [],
      supplier: [],
      recommendation: [],
      report: [],
    };

    filteredResults.forEach((result) => {
      groups[result.type].push(result);
    });

    return Object.entries(groups).filter(([_, items]) => items.length > 0);
  }, [filteredResults]);

  const handleSelect = useCallback(
    (result: SearchResult) => {
      // Add to recent searches
      setRecentSearches((prev) => {
        const newSearches = [searchQuery, ...prev.filter((s) => s !== searchQuery)];
        return newSearches.slice(0, 5); // Keep only last 5 searches
      });

      // Navigate to the result
      router.push(result.url);
      setOpen(false);
      setSearchQuery("");
    },
    [router, searchQuery]
  );

  const handleRecentSearchClick = (query: string) => {
    setSearchQuery(query);
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query})`, "gi"));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 dark:bg-yellow-900">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="w-full max-w-xl">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search alerts, suppliers, reports..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
              className="pl-10 pr-10"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2"
                onClick={() => {
                  setSearchQuery("");
                  setOpen(false);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </PopoverTrigger>
        <PopoverContent
          className="w-[560px] p-0"
          align="start"
          onOpenAutoFocus={(e) => e.preventDefault()}
        >
          <Command>
            <CommandList>
              {/* Recent Searches */}
              {!searchQuery && recentSearches.length > 0 && (
                <>
                  <CommandGroup heading="Recent Searches">
                    {recentSearches.map((query, index) => (
                      <CommandItem
                        key={index}
                        onSelect={() => handleRecentSearchClick(query)}
                        className="cursor-pointer"
                      >
                        <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
                        <span>{query}</span>
                      </CommandItem>
                    ))}
                  </CommandGroup>
                  <CommandSeparator />
                  <div className="p-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full text-xs"
                      onClick={clearRecentSearches}
                    >
                      Clear recent searches
                    </Button>
                  </div>
                </>
              )}

              {/* Search Results */}
              {searchQuery && searchQuery.length >= 2 && (
                <>
                  {filteredResults.length === 0 ? (
                    <CommandEmpty>
                      <div className="text-center py-6">
                        <Search className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                        <p className="text-sm text-muted-foreground">
                          No results found for &quot;{searchQuery}&quot;
                        </p>
                      </div>
                    </CommandEmpty>
                  ) : (
                    groupedResults.map(([type, results]) => (
                      <CommandGroup
                        key={type}
                        heading={`${getResultTypeLabel(type as SearchResult["type"])}s`}
                      >
                        {results.map((result) => (
                          <CommandItem
                            key={result.id}
                            onSelect={() => handleSelect(result)}
                            className="cursor-pointer"
                          >
                            <div className="flex items-start gap-3 w-full">
                              {getResultIcon(result.type)}
                              <div className="flex-1 space-y-1">
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium">
                                    {highlightMatch(result.title, searchQuery)}
                                  </p>
                                  <Badge
                                    variant="secondary"
                                    className="text-xs"
                                  >
                                    {getResultTypeLabel(result.type)}
                                  </Badge>
                                </div>
                                {result.description && (
                                  <p className="text-xs text-muted-foreground line-clamp-1">
                                    {highlightMatch(result.description, searchQuery)}
                                  </p>
                                )}
                                {result.tags && result.tags.length > 0 && (
                                  <div className="flex gap-1 flex-wrap">
                                    {result.tags.map((tag) => (
                                      <Badge
                                        key={tag}
                                        variant="outline"
                                        className="text-xs"
                                      >
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    ))
                  )}
                </>
              )}

              {/* Initial state */}
              {!searchQuery && recentSearches.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <Search className="mx-auto h-12 w-12 mb-3 opacity-20" />
                  <p className="text-sm">Start typing to search...</p>
                  <p className="text-xs mt-1">Search for alerts, suppliers, reports, and more</p>
                </div>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}