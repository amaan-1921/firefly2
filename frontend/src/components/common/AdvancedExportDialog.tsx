'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Download, FileText, FileSpreadsheet, File } from 'lucide-react';

type ExportFormat = 'csv' | 'excel' | 'pdf' | 'json';
type DateRange = 'all' | 'last7days' | 'last30days' | 'last90days' | 'custom';

interface ExportField {
  id: string;
  label: string;
  selected: boolean;
}

interface AdvancedExportDialogProps {
  trigger?: React.ReactNode;
  dataType?: string;
  onExport?: (config: ExportConfig) => void;
}

interface ExportConfig {
  format: ExportFormat;
  fields: string[];
  dateRange: DateRange;
  includeHeaders: boolean;
  includeMetadata: boolean;
}

const defaultFields: ExportField[] = [
  { id: 'id', label: 'ID', selected: true },
  { id: 'name', label: 'Name', selected: true },
  { id: 'status', label: 'Status', selected: true },
  { id: 'score', label: 'Risk Score', selected: true },
  { id: 'category', label: 'Category', selected: true },
  { id: 'lastUpdated', label: 'Last Updated', selected: true },
  { id: 'description', label: 'Description', selected: false },
  { id: 'assignee', label: 'Assignee', selected: false },
  { id: 'tags', label: 'Tags', selected: false },
  { id: 'notes', label: 'Notes', selected: false },
];

const formatIcons = {
  csv: FileText,
  excel: FileSpreadsheet,
  pdf: File,
  json: FileText,
};

export default function AdvancedExportDialog({
  trigger,

  onExport
}: AdvancedExportDialogProps) {
  const [open, setOpen] = useState(false);
  const [format, setFormat] = useState<ExportFormat>('csv');
  const [dateRange, setDateRange] = useState<DateRange>('all');
  const [fields, setFields] = useState<ExportField[]>(defaultFields);
  const [includeHeaders, setIncludeHeaders] = useState(true);
  const [includeMetadata, setIncludeMetadata] = useState(false);

  const handleFieldToggle = (fieldId: string) => {
    setFields(
      fields.map((field) =>
        field.id === fieldId ? { ...field, selected: !field.selected } : field
      )
    );
  };

  const selectAllFields = () => {
    setFields(fields.map((field) => ({ ...field, selected: true })));
  };

  const deselectAllFields = () => {
    setFields(fields.map((field) => ({ ...field, selected: false })));
  };

  const handleExport = () => {
    const selectedFields = fields.filter((f) => f.selected).map((f) => f.id);
    
    const config: ExportConfig = {
      format,
      fields: selectedFields,
      dateRange,
      includeHeaders,
      includeMetadata,
    };

    onExport?.(config);
    setOpen(false);
  };

  const FormatIcon = formatIcons[format];
  const selectedCount = fields.filter((f) => f.selected).length;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Advanced Export Options</DialogTitle>
          <DialogDescription>
            Customize your export by selecting the format, fields, and date range.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Format Selection */}
          <div>
            <Label className="text-base font-semibold mb-3 block">Export Format</Label>
            <RadioGroup value={format} onValueChange={(value) => setFormat(value as ExportFormat)}>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:bg-accent">
                  <RadioGroupItem value="csv" id="csv" />
                  <Label htmlFor="csv" className="flex items-center gap-2 cursor-pointer flex-1">
                    <FileText className="h-4 w-4" />
                    <div>
                      <div className="font-medium">CSV</div>
                      <div className="text-xs text-muted-foreground">Comma-separated values</div>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:bg-accent">
                  <RadioGroupItem value="excel" id="excel" />
                  <Label htmlFor="excel" className="flex items-center gap-2 cursor-pointer flex-1">
                    <FileSpreadsheet className="h-4 w-4" />
                    <div>
                      <div className="font-medium">Excel</div>
                      <div className="text-xs text-muted-foreground">XLSX spreadsheet</div>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:bg-accent">
                  <RadioGroupItem value="pdf" id="pdf" />
                  <Label htmlFor="pdf" className="flex items-center gap-2 cursor-pointer flex-1">
                    <File className="h-4 w-4" />
                    <div>
                      <div className="font-medium">PDF</div>
                      <div className="text-xs text-muted-foreground">Formatted document</div>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:bg-accent">
                  <RadioGroupItem value="json" id="json" />
                  <Label htmlFor="json" className="flex items-center gap-2 cursor-pointer flex-1">
                    <FileText className="h-4 w-4" />
                    <div>
                      <div className="font-medium">JSON</div>
                      <div className="text-xs text-muted-foreground">Structured data</div>
                    </div>
                  </Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Date Range Selection */}
          <div>
            <Label className="text-base font-semibold mb-3 block">Date Range</Label>
            <Select value={dateRange} onValueChange={(value) => setDateRange(value as DateRange)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Time</SelectItem>
                <SelectItem value="last7days">Last 7 Days</SelectItem>
                <SelectItem value="last30days">Last 30 Days</SelectItem>
                <SelectItem value="last90days">Last 90 Days</SelectItem>
                <SelectItem value="custom">Custom Range</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Field Selection */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-base font-semibold">
                Fields to Export
                <Badge variant="outline" className="ml-2">
                  {selectedCount} selected
                </Badge>
              </Label>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={selectAllFields}
                >
                  Select All
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={deselectAllFields}
                >
                  Deselect All
                </Button>
              </div>
            </div>
            <div className="border rounded-lg p-4 max-h-64 overflow-y-auto">
              <div className="grid grid-cols-2 gap-3">
                {fields.map((field) => (
                  <div key={field.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={field.id}
                      checked={field.selected}
                      onCheckedChange={() => handleFieldToggle(field.id)}
                    />
                    <Label
                      htmlFor={field.id}
                      className="text-sm font-normal cursor-pointer"
                    >
                      {field.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Additional Options */}
          <div>
            <Label className="text-base font-semibold mb-3 block">Additional Options</Label>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="headers"
                  checked={includeHeaders}
                  onCheckedChange={(checked) => setIncludeHeaders(!!checked)}
                />
                <Label htmlFor="headers" className="text-sm font-normal cursor-pointer">
                  Include column headers
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="metadata"
                  checked={includeMetadata}
                  onCheckedChange={(checked) => setIncludeMetadata(!!checked)}
                />
                <Label htmlFor="metadata" className="text-sm font-normal cursor-pointer">
                  Include metadata (export date, filters applied, etc.)
                </Label>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={selectedCount === 0}>
            <FormatIcon className="h-4 w-4 mr-2" />
            Export {format.toUpperCase()}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}