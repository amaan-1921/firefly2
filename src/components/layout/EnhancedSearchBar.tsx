'use client';

import React, { useState, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Search, X, Filter, Clock, TrendingUp } from 'lucide-react';

interface SearchFilter {
  key: string;
  label: string;
  value: string;
}

interface EnhancedSearchBarProps {
  placeholder?: string;
  onSearch?: (query: string, filters: SearchFilter[]) => void;
  recentSearches?: string[];
  suggestions?: string[];
  filters?: SearchFilter[];
}

export default function EnhancedSearchBar({
  placeholder = 'Search risks, suppliers, alerts...',
  onSearch,
  recentSearches = [],
  suggestions = [],
}: EnhancedSearchBarProps) {
  const [query, setQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<SearchFilter[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const defaultRecentSearches = [
    'Critical suppliers',
    'High risk alerts',
    'Port delays',
    'Financial risks'
  ];

  const defaultSuggestions = [
    'Critical risks in Asia Pacific',
    'Supplier payment delays',
    'Geopolitical tensions Europe',
    'Weather-related disruptions',
    'Compliance violations'
  ];

  const availableFilters: SearchFilter[] = [
    { key: 'status', label: 'Status', value: 'critical' },
    { key: 'status', label: 'Status', value: 'high' },
    { key: 'category', label: 'Category', value: 'financial' },
    { key: 'category', label: 'Category', value: 'geopolitical' },
    { key: 'type', label: 'Type', value: 'supplier' },
    { key: 'type', label: 'Type', value: 'port' },
  ];

  const displayedRecentSearches = recentSearches.length > 0 ? recentSearches : defaultRecentSearches;
  const displayedSuggestions = suggestions.length > 0 ? suggestions : defaultSuggestions;

  const handleSearch = (searchQuery?: string) => {
    const finalQuery = searchQuery || query;
    if (finalQuery.trim() || activeFilters.length > 0) {
      onSearch?.(finalQuery, activeFilters);
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const addFilter = (filter: SearchFilter) => {
    const exists = activeFilters.some(
      (f) => f.key === filter.key && f.value === filter.value
    );
    if (!exists) {
      setActiveFilters([...activeFilters, filter]);
    }
    setShowFilters(false);
  };

  const removeFilter = (index: number) => {
    setActiveFilters(activeFilters.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setQuery('');
    setActiveFilters([]);
  };

  return (
    <div className="w-full max-w-3xl">
      <div className="relative">
        <div className="flex items-center gap-2 p-3 border rounded-lg bg-background shadow-sm focus-within:ring-2 focus-within:ring-ring">
          <Search className="h-5 w-5 text-muted-foreground flex-shrink-0" />

          <div className="flex-1 flex flex-wrap items-center gap-2">
            {activeFilters.map((filter, index) => (
              <Badge
                key={index}
                variant="secondary"
                className="gap-1 pr-1"
              >
                <span className="text-xs">
                  {filter.label}: {filter.value}
                </span>
                <button
                  onClick={() => removeFilter(index)}
                  className="hover:bg-secondary-foreground/20 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}

            <Input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowSuggestions(true)}
              className="border-none shadow-none focus-visible:ring-0 p-0 h-auto flex-1 min-w-[200px]"
            />
          </div>

          <div className="flex items-center gap-1 flex-shrink-0">
            {(query || activeFilters.length > 0) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}

            <Popover open={showFilters} onOpenChange={setShowFilters}>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-2 h-8">
                  <Filter className="h-4 w-4" />
                  Filters
                  {activeFilters.length > 0 && (
                    <Badge variant="secondary" className="h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                      {activeFilters.length}
                    </Badge>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-64 p-0" align="end">
                <Command>
                  <CommandInput placeholder="Search filters..." />
                  <CommandList>
                    <CommandEmpty>No filters found.</CommandEmpty>
                    <CommandGroup heading="Available Filters">
                      {availableFilters.map((filter, index) => (
                        <CommandItem
                          key={index}
                          onSelect={() => addFilter(filter)}
                        >
                          <span className="text-sm">
                            <span className="text-muted-foreground">{filter.label}:</span>{' '}
                            <span className="font-medium">{filter.value}</span>
                          </span>
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>

            <Button
              onClick={() => handleSearch()}
              size="sm"
              className="h-8"
            >
              Search
            </Button>
          </div>
        </div>

        {/* Search Suggestions Dropdown */}
        {showSuggestions && !query && (
          <div className="absolute top-full mt-2 w-full bg-background border rounded-lg shadow-lg z-50">
            <div className="p-2">
              {displayedRecentSearches.length > 0 && (
                <div className="mb-3">
                  <div className="flex items-center gap-2 px-2 py-1 text-sm font-medium text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    Recent Searches
                  </div>
                  {displayedRecentSearches.slice(0, 4).map((search, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setQuery(search);
                        handleSearch(search);
                      }}
                      className="w-full text-left px-2 py-2 hover:bg-accent rounded text-sm"
                    >
                      {search}
                    </button>
                  ))}
                </div>
              )}

              {displayedSuggestions.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 px-2 py-1 text-sm font-medium text-muted-foreground">
                    <TrendingUp className="h-4 w-4" />
                    Suggested Searches
                  </div>
                  {displayedSuggestions.slice(0, 5).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setQuery(suggestion);
                        handleSearch(suggestion);
                      }}
                      className="w-full text-left px-2 py-2 hover:bg-accent rounded text-sm"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}