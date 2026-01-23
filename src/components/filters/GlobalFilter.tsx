"use client";

import { useState } from "react";
import { Filter, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";

export interface FilterState {
  severity: string[];
  category: string[];
  status: string[];
  supplier: string[];
  location: string[];
}

interface GlobalFilterProps {
  onFilterChange?: (filters: FilterState) => void;
  className?: string;
}

const severityOptions = [
  { label: "Critical", value: "critical", color: "destructive" },
  { label: "High", value: "high", color: "destructive" },
  { label: "Medium", value: "medium", color: "default" },
  { label: "Low", value: "low", color: "secondary" },
];

const categoryOptions = [
  { label: "Supply Chain", value: "supply_chain" },
  { label: "Logistics", value: "logistics" },
  { label: "Manufacturing", value: "manufacturing" },
  { label: "Procurement", value: "procurement" },
  { label: "Quality", value: "quality" },
  { label: "Financial", value: "financial" },
];

const statusOptions = [
  { label: "Open", value: "open" },
  { label: "In Progress", value: "in_progress" },
  { label: "Resolved", value: "resolved" },
  { label: "Closed", value: "closed" },
];

const supplierOptions = [
  { label: "ABC Manufacturing", value: "abc_manufacturing" },
  { label: "XYZ Logistics", value: "xyz_logistics" },
  { label: "Global Suppliers Inc", value: "global_suppliers" },
  { label: "Tech Components Ltd", value: "tech_components" },
];

const locationOptions = [
  { label: "North America", value: "north_america" },
  { label: "Europe", value: "europe" },
  { label: "Asia Pacific", value: "asia_pacific" },
  { label: "Latin America", value: "latin_america" },
  { label: "Middle East", value: "middle_east" },
];

export function GlobalFilter({ onFilterChange, className }: GlobalFilterProps) {
  const [open, setOpen] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    severity: [],
    category: [],
    status: [],
    supplier: [],
    location: [],
  });

  const [savedPresets] = useState<{ name: string; filters: FilterState }[]>([
    {
      name: "Critical Issues",
      filters: {
        severity: ["critical", "high"],
        category: [],
        status: ["open", "in_progress"],
        supplier: [],
        location: [],
      },
    },
  ]);

  const handleCheckboxChange = (filterType: keyof FilterState, value: string, checked: boolean) => {
    setFilters((prev) => {
      const currentValues = prev[filterType];
      const newValues = checked
        ? [...currentValues, value]
        : currentValues.filter((v) => v !== value);

      const newFilters = { ...prev, [filterType]: newValues };
      onFilterChange?.(newFilters);
      return newFilters;
    });
  };

  const getActiveFilterCount = () => {
    return Object.values(filters).reduce((acc, curr) => acc + curr.length, 0);
  };

  const clearAllFilters = () => {
    const emptyFilters: FilterState = {
      severity: [],
      category: [],
      status: [],
      supplier: [],
      location: [],
    };
    setFilters(emptyFilters);
    onFilterChange?.(emptyFilters);
  };

  const applyPreset = (preset: { name: string; filters: FilterState }) => {
    setFilters(preset.filters);
    onFilterChange?.(preset.filters);
  };

  const activeCount = getActiveFilterCount();

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" className={className}>
          <Filter className="h-4 w-4 mr-2" />
          Filters
          {activeCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeCount}
            </Badge>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Filter Options</SheetTitle>
          <SheetDescription>
            Apply filters to refine your dashboard data
          </SheetDescription>
        </SheetHeader>

        <div className="py-6 space-y-6">
          {/* Saved Presets */}
          {savedPresets.length > 0 && (
            <>
              <div className="space-y-2">
                <Label>Saved Presets</Label>
                <div className="flex flex-wrap gap-2">
                  {savedPresets.map((preset) => (
                    <Button
                      key={preset.name}
                      variant="outline"
                      size="sm"
                      onClick={() => applyPreset(preset)}
                    >
                      {preset.name}
                    </Button>
                  ))}
                </div>
              </div>
              <Separator />
            </>
          )}

          {/* Severity Filter */}
          <div className="space-y-3">
            <Label>Severity</Label>
            <div className="space-y-2">
              {severityOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`severity-${option.value}`}
                    checked={filters.severity.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("severity", option.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`severity-${option.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Category Filter */}
          <div className="space-y-3">
            <Label>Category</Label>
            <div className="space-y-2">
              {categoryOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`category-${option.value}`}
                    checked={filters.category.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("category", option.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`category-${option.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Status Filter */}
          <div className="space-y-3">
            <Label>Status</Label>
            <div className="space-y-2">
              {statusOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`status-${option.value}`}
                    checked={filters.status.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("status", option.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`status-${option.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Supplier Filter */}
          <div className="space-y-3">
            <Label>Supplier</Label>
            <div className="space-y-2">
              {supplierOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`supplier-${option.value}`}
                    checked={filters.supplier.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("supplier", option.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`supplier-${option.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Location Filter */}
          <div className="space-y-3">
            <Label>Location</Label>
            <div className="space-y-2">
              {locationOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`location-${option.value}`}
                    checked={filters.location.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("location", option.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`location-${option.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>

        <SheetFooter className="flex flex-row gap-2">
          <Button variant="outline" onClick={clearAllFilters} className="flex-1">
            <RotateCcw className="h-4 w-4 mr-2" />
            Clear All
          </Button>
          <Button onClick={() => setOpen(false)} className="flex-1">
            Apply Filters
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}