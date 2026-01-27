'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  AlertCircle,
  FileText,
  UserPlus,
  Download,
  Bell,
  TrendingUp,
  Settings,
} from 'lucide-react';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick?: () => void;
  badge?: string;
  variant?: 'default' | 'destructive' | 'outline';
}

interface QuickActionsPanelProps {
  actions?: QuickAction[];
  title?: string;
  onActionClick?: (actionId: string) => void;
}

const defaultActions: QuickAction[] = [
  {
    id: 'new-alert',
    title: 'Create Alert',
    description: 'Report a new risk or issue',
    icon: <Plus className="h-5 w-5" />,
    variant: 'default',
  },
  {
    id: 'critical-risks',
    title: 'Review Critical Risks',
    description: 'View high priority items',
    icon: <AlertCircle className="h-5 w-5" />,
    variant: 'destructive',
    badge: '5',
  },
  {
    id: 'generate-report',
    title: 'Generate Report',
    description: 'Create summary report',
    icon: <FileText className="h-5 w-5" />,
    variant: 'outline',
  },
  {
    id: 'add-supplier',
    title: 'Add Supplier',
    description: 'Onboard new supplier',
    icon: <UserPlus className="h-5 w-5" />,
    variant: 'outline',
  },
  {
    id: 'export-data',
    title: 'Export Data',
    description: 'Download current view',
    icon: <Download className="h-5 w-5" />,
    variant: 'outline',
  },
  {
    id: 'notifications',
    title: 'Notifications',
    description: 'View all notifications',
    icon: <Bell className="h-5 w-5" />,
    variant: 'outline',
    badge: '12',
  },
  {
    id: 'analytics',
    title: 'View Analytics',
    description: 'Access detailed analytics',
    icon: <TrendingUp className="h-5 w-5" />,
    variant: 'outline',
  },
  {
    id: 'settings',
    title: 'Settings',
    description: 'Manage preferences',
    icon: <Settings className="h-5 w-5" />,
    variant: 'outline',
  },
];

export default function QuickActionsPanel({
  actions = defaultActions,
  title = 'Quick Actions',
  onActionClick,
}: QuickActionsPanelProps) {
  const handleClick = (action: QuickAction) => {
    onActionClick?.(action.id);
    action.onClick?.();
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {actions.map((action) => (
          <Button
            key={action.id}
            variant={action.variant || 'outline'}
            onClick={() => handleClick(action)}
            className="h-auto flex-col items-start p-4 relative"
          >
            <div className="flex items-center justify-between w-full mb-2">
              <div className="flex items-center gap-2">
                {action.icon}
                {action.badge && (
                  <Badge variant="secondary" className="text-xs">
                    {action.badge}
                  </Badge>
                )}
              </div>
            </div>
            <div className="text-left w-full">
              <div className="font-semibold text-sm mb-1">{action.title}</div>
              <div className="text-xs text-muted-foreground font-normal">
                {action.description}
              </div>
            </div>
          </Button>
        ))}
      </div>
    </Card>
  );
}