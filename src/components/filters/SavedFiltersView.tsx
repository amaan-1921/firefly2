'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Save, Star, StarOff, MoreVertical, Trash2 } from 'lucide-react';

interface FilterPreset {
  id: string;
  name: string;
  filters: Record<string, any>;
  favorite: boolean;
  createdAt: string;
  usageCount: number;
}

interface SavedFiltersViewProps {
  currentFilters?: Record<string, any>;
  onApplyFilter?: (filters: Record<string, any>) => void;
  presets?: FilterPreset[];
}

const mockPresets: FilterPreset[] = [
  {
    id: '1',
    name: 'Critical Risks Only',
    filters: { status: 'critical', category: 'all' },
    favorite: true,
    createdAt: '2024-01-10',
    usageCount: 45
  },
  {
    id: '2',
    name: 'Financial Risks - Last 7 Days',
    filters: { category: 'financial', dateRange: 'last7days' },
    favorite: true,
    createdAt: '2024-01-12',
    usageCount: 32
  },
  {
    id: '3',
    name: 'Active Suppliers',
    filters: { type: 'supplier', status: ['high', 'critical'] },
    favorite: false,
    createdAt: '2024-01-08',
    usageCount: 18
  },
  {
    id: '4',
    name: 'Geopolitical Alerts',
    filters: { category: 'geopolitical', score: { min: 50 } },
    favorite: false,
    createdAt: '2024-01-05',
    usageCount: 12
  }
];

export default function SavedFiltersView({
  currentFilters = {},
  onApplyFilter,
  presets = mockPresets
}: SavedFiltersViewProps) {
  const [filterPresets, setFilterPresets] = useState<FilterPreset[]>(presets);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newPresetName, setNewPresetName] = useState('');

  const handleSaveFilter = () => {
    if (!newPresetName.trim()) return;

    const newPreset: FilterPreset = {
      id: Date.now().toString(),
      name: newPresetName,
      filters: currentFilters,
      favorite: false,
      createdAt: new Date().toISOString().split('T')[0],
      usageCount: 0
    };

    setFilterPresets([...filterPresets, newPreset]);
    setNewPresetName('');
    setIsDialogOpen(false);
  };

  const toggleFavorite = (id: string) => {
    setFilterPresets(
      filterPresets.map((preset) =>
        preset.id === id ? { ...preset, favorite: !preset.favorite } : preset
      )
    );
  };

  const deletePreset = (id: string) => {
    setFilterPresets(filterPresets.filter((preset) => preset.id !== id));
  };

  const applyFilter = (preset: FilterPreset) => {
    setFilterPresets(
      filterPresets.map((p) =>
        p.id === preset.id ? { ...p, usageCount: p.usageCount + 1 } : p
      )
    );
    onApplyFilter?.(preset.filters);
  };

  const favoritePresets = filterPresets.filter((p) => p.favorite);
  const otherPresets = filterPresets.filter((p) => !p.favorite);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Saved Filter Views</h3>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save Current Filter
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Save Filter Preset</DialogTitle>
              <DialogDescription>
                Give your filter preset a descriptive name to reuse it later.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Input
                placeholder="e.g., High Risk Suppliers"
                value={newPresetName}
                onChange={(e) => setNewPresetName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSaveFilter()}
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveFilter} disabled={!newPresetName.trim()}>
                Save Preset
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {favoritePresets.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            Favorites
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {favoritePresets.map((preset) => (
              <Card
                key={preset.id}
                className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => applyFilter(preset)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="font-semibold text-sm">{preset.name}</h5>
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {Object.entries(preset.filters).slice(0, 2).map(([key, value]) => (
                        <Badge key={key} variant="secondary" className="text-xs">
                          {key}: {String(value)}
                        </Badge>
                      ))}
                      {Object.keys(preset.filters).length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{Object.keys(preset.filters).length - 2}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      Used {preset.usageCount} times
                    </p>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(preset.id);
                        }}
                      >
                        <StarOff className="h-4 w-4 mr-2" />
                        Remove from Favorites
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          deletePreset(preset.id);
                        }}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {otherPresets.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            All Saved Filters
          </h4>
          <div className="space-y-2">
            {otherPresets.map((preset) => (
              <Card
                key={preset.id}
                className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => applyFilter(preset)}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="font-semibold text-sm">{preset.name}</h5>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {Object.entries(preset.filters).slice(0, 3).map(([key, value]) => (
                        <Badge key={key} variant="secondary" className="text-xs">
                          {key}: {String(value)}
                        </Badge>
                      ))}
                      {Object.keys(preset.filters).length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{Object.keys(preset.filters).length - 3}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Created {preset.createdAt} • Used {preset.usageCount} times
                    </p>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(preset.id);
                        }}
                      >
                        <Star className="h-4 w-4 mr-2" />
                        Add to Favorites
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          deletePreset(preset.id);
                        }}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {filterPresets.length === 0 && (
        <div className="text-center py-12">
          <Save className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">
            No saved filters yet. Save your current filter settings to reuse them later.
          </p>
        </div>
      )}
    </div>
  );
}