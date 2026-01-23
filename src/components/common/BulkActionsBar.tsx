'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  CheckCircle,
  XCircle,
  Archive,
  Trash2,
  Tag,
  UserPlus,
  MoreVertical,
  X,
} from 'lucide-react';

interface BulkActionsBarProps {
  selectedCount: number;
  onClearSelection?: () => void;
  onMarkResolved?: () => void;
  onMarkUnresolved?: () => void;
  onArchive?: () => void;
  onDelete?: () => void;
  onAssign?: () => void;
  onAddTags?: () => void;
}

export default function BulkActionsBar({
  selectedCount,
  onClearSelection,
  onMarkResolved,
  onMarkUnresolved,
  onArchive,
  onDelete,
  onAssign,
  onAddTags,
}: BulkActionsBarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
      <div className="bg-background border shadow-lg rounded-lg p-4 flex items-center gap-4 animate-in slide-in-from-bottom-5">
        {/* Selection Count */}
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-base px-3 py-1">
            {selectedCount} selected
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearSelection}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="h-6 w-px bg-border" />

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onMarkResolved}
            className="gap-2"
          >
            <CheckCircle className="h-4 w-4" />
            Mark Resolved
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onMarkUnresolved}
            className="gap-2"
          >
            <XCircle className="h-4 w-4" />
            Mark Unresolved
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onArchive}
            className="gap-2"
          >
            <Archive className="h-4 w-4" />
            Archive
          </Button>
        </div>

        {/* More Actions Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2">
              <MoreVertical className="h-4 w-4" />
              More Actions
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem onClick={onAssign}>
              <UserPlus className="h-4 w-4 mr-2" />
              Assign to User
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onAddTags}>
              <Tag className="h-4 w-4 mr-2" />
              Add Tags
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={onDelete}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Selected
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}