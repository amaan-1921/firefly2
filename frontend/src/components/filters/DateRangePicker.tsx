"use client";

import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { DateRange } from "react-day-picker";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DateRangePickerProps {
  className?: string;
  onDateChange?: (range: DateRange | undefined) => void;
  defaultRange?: DateRange;
}

type PresetRange = "today" | "yesterday" | "last7days" | "last30days" | "last90days" | "thisMonth" | "lastMonth" | "custom";

const getPresetRange = (preset: PresetRange): DateRange | undefined => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  switch (preset) {
    case "today":
      return { from: today, to: today };
    case "yesterday":
      return { from: yesterday, to: yesterday };
    case "last7days":
      const last7 = new Date(today);
      last7.setDate(last7.getDate() - 7);
      return { from: last7, to: today };
    case "last30days":
      const last30 = new Date(today);
      last30.setDate(last30.getDate() - 30);
      return { from: last30, to: today };
    case "last90days":
      const last90 = new Date(today);
      last90.setDate(last90.getDate() - 90);
      return { from: last90, to: today };
    case "thisMonth":
      const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
      return { from: thisMonthStart, to: today };
    case "lastMonth":
      const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
      return { from: lastMonthStart, to: lastMonthEnd };
    default:
      return undefined;
  }
};

const presetOptions = [
  { label: "Today", value: "today" },
  { label: "Yesterday", value: "yesterday" },
  { label: "Last 7 days", value: "last7days" },
  { label: "Last 30 days", value: "last30days" },
  { label: "Last 90 days", value: "last90days" },
  { label: "This month", value: "thisMonth" },
  { label: "Last month", value: "lastMonth" },
  { label: "Custom range", value: "custom" },
];

export function DateRangePicker({
  className,
  onDateChange,
  defaultRange,
}: DateRangePickerProps) {
  const [date, setDate] = React.useState<DateRange | undefined>(defaultRange);
  const [preset, setPreset] = React.useState<PresetRange>("last30days");

  React.useEffect(() => {
    if (preset !== "custom") {
      const newRange = getPresetRange(preset);
      setDate(newRange);
      onDateChange?.(newRange);
    }
  }, [preset, onDateChange]);

  const handleDateSelect = (newDate: DateRange | undefined) => {
    setDate(newDate);
    setPreset("custom");
    onDateChange?.(newDate);
  };

  const handlePresetChange = (value: PresetRange) => {
    setPreset(value);
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-full justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "LLL dd, y")} -{" "}
                  {format(date.to, "LLL dd, y")}
                </>
              ) : (
                format(date.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date range</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="p-3 border-b">
            <Select value={preset} onValueChange={handlePresetChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select preset" />
              </SelectTrigger>
              <SelectContent>
                {presetOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={date?.from}
            selected={date}
            onSelect={handleDateSelect}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}