'use client';

import React from 'react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { HelpCircle, Info, BookOpen, ExternalLink } from 'lucide-react';

interface HelpContent {
  title: string;
  description: string;
  steps?: string[];
  tips?: string[];
  link?: {
    text: string;
    url: string;
  };
}

interface ContextualHelpProps {
  content: HelpContent;
  type?: 'tooltip' | 'popover';
  icon?: 'help' | 'info' | 'book';
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export function ContextualHelp({
  content,
  type = 'tooltip',
  icon = 'help',
  side = 'top',
}: ContextualHelpProps) {
  const IconComponent = {
    help: HelpCircle,
    info: Info,
    book: BookOpen,
  }[icon];

  if (type === 'tooltip') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <button className="inline-flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
              <IconComponent className="h-4 w-4" />
            </button>
          </TooltipTrigger>
          <TooltipContent side={side} className="max-w-xs">
            <p className="font-medium">{content.title}</p>
            <p className="text-sm text-muted-foreground mt-1">{content.description}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="inline-flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
          <IconComponent className="h-4 w-4" />
        </button>
      </PopoverTrigger>
      <PopoverContent side={side} className="w-80">
        <div className="space-y-3">
          <div>
            <h4 className="font-semibold text-base mb-1">{content.title}</h4>
            <p className="text-sm text-muted-foreground">{content.description}</p>
          </div>

          {content.steps && content.steps.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Steps:</p>
              <ol className="list-decimal list-inside space-y-1">
                {content.steps.map((step, index) => (
                  <li key={index} className="text-sm text-muted-foreground">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {content.tips && content.tips.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2 flex items-center gap-1">
                <Info className="h-3 w-3" />
                Tips:
              </p>
              <ul className="space-y-1">
                {content.tips.map((tip, index) => (
                  <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className="mt-1.5 h-1 w-1 rounded-full bg-muted-foreground flex-shrink-0" />
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {content.link && (
            <a
              href={content.link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-primary hover:underline"
            >
              {content.link.text}
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Pre-configured help sections for common features
export const HelpSections = {
  riskScore: {
    title: 'Risk Score',
    description: 'A numerical value (0-100) representing the overall risk level. Higher scores indicate greater risk.',
    tips: [
      'Scores above 70 are considered high risk',
      'Scores are updated daily based on multiple factors',
      'Click on a risk to see detailed breakdown'
    ]
  },
  filters: {
    title: 'Using Filters',
    description: 'Narrow down your results by applying multiple filter criteria.',
    steps: [
      'Select filter categories from the sidebar',
      'Choose specific values or ranges',
      'Click "Apply" to update results',
      'Save commonly used filters for quick access'
    ],
    link: {
      text: 'Learn more about advanced filtering',
      url: '#'
    }
  },
  export: {
    title: 'Exporting Data',
    description: 'Download your data in various formats for external analysis.',
    steps: [
      'Click the Export button',
      'Choose your preferred format (CSV, Excel, PDF)',
      'Select which fields to include',
      'Confirm and download'
    ],
    tips: [
      'CSV format works best for data analysis',
      'PDF format is ideal for reports',
      'You can customize which columns to export'
    ]
  },
  bulkActions: {
    title: 'Bulk Actions',
    description: 'Perform actions on multiple items at once to save time.',
    steps: [
      'Select items using checkboxes',
      'Choose an action from the bulk actions bar',
      'Confirm your selection',
      'Changes are applied to all selected items'
    ],
    tips: [
      'Use "Select All" to quickly select all visible items',
      'You can undo most bulk actions',
      'Be careful with delete and archive actions'
    ]
  },
  dashboard: {
    title: 'Dashboard Customization',
    description: 'Personalize your dashboard by rearranging widgets and choosing which metrics to display.',
    steps: [
      'Click the customize button',
      'Drag widgets to reorder',
      'Toggle widgets on/off',
      'Save your layout'
    ],
    tips: [
      'Create different layouts for different workflows',
      'Your preferences are saved automatically',
      'Reset to default layout anytime'
    ]
  }
};

export default ContextualHelp;