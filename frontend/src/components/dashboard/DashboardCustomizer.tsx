'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Settings, GripVertical, Eye, EyeOff, RotateCcw } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface Widget {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  order: number;
}

interface DashboardCustomizerProps {
  onSaveLayout?: (widgets: Widget[]) => void;
  initialWidgets?: Widget[];
}

const defaultWidgets: Widget[] = [
  { id: 'risk-snapshot', name: 'Risk Snapshot', description: 'Overview of current risk levels', enabled: true, order: 1 },
  { id: 'kpi-cards', name: 'KPI Cards', description: 'Key performance indicators', enabled: true, order: 2 },
  { id: 'recent-alerts', name: 'Recent Alerts', description: 'Latest risk alerts', enabled: true, order: 3 },
  { id: 'world-map', name: 'World Map', description: 'Geographic risk distribution', enabled: true, order: 4 },
  { id: 'traffic-light', name: 'Traffic Light View', description: 'Risk status indicators', enabled: false, order: 5 },
  { id: 'risk-timeline', name: 'Risk Progression Timeline', description: 'Historical risk changes', enabled: false, order: 6 },
  { id: 'chart-widgets', name: 'Chart Widgets', description: 'Visual analytics', enabled: true, order: 7 },
];

export default function DashboardCustomizer({
  onSaveLayout,
  initialWidgets = defaultWidgets
}: DashboardCustomizerProps) {
  const [open, setOpen] = useState(false);
  const [widgets, setWidgets] = useState<Widget[]>(initialWidgets);

  const toggleWidget = (id: string) => {
    setWidgets(widgets.map(w => w.id === id ? { ...w, enabled: !w.enabled } : w));
  };

  const resetToDefault = () => {
    setWidgets(defaultWidgets);
  };

  const handleSave = () => {
    onSaveLayout?.(widgets);
    setOpen(false);
  };

  const enabledCount = widgets.filter(w => w.enabled).length;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings className="h-4 w-4" />
          Customize Dashboard
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Customize Your Dashboard</DialogTitle>
          <DialogDescription>
            Choose which widgets to display on your dashboard. Your preferences are saved automatically.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {enabledCount} of {widgets.length} widgets enabled
            </p>
            <Button variant="ghost" size="sm" onClick={resetToDefault} className="gap-2">
              <RotateCcw className="h-4 w-4" />
              Reset to Default
            </Button>
          </div>

          <div className="space-y-2">
            {widgets.map((widget) => (
              <Card key={widget.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <GripVertical className="h-5 w-5 text-muted-foreground cursor-move" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Label htmlFor={widget.id} className="font-medium cursor-pointer">
                          {widget.name}
                        </Label>
                        {widget.enabled ? (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {widget.description}
                      </p>
                    </div>
                  </div>
                  <Switch
                    id={widget.id}
                    checked={widget.enabled}
                    onCheckedChange={() => toggleWidget(widget.id)}
                  />
                </div>
              </Card>
            ))}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            Save Layout
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}