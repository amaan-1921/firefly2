'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowUp, ArrowDown, Minus, TrendingUp } from 'lucide-react';

interface TimelineEvent {
  id: string;
  date: string;
  riskName: string;
  previousStatus: 'critical' | 'high' | 'medium' | 'low';
  currentStatus: 'critical' | 'high' | 'medium' | 'low';
  previousScore: number;
  currentScore: number;
  description: string;
}

interface RiskProgressionTimelineProps {
  events?: TimelineEvent[];
  maxEvents?: number;
}

const mockEvents: TimelineEvent[] = [
  {
    id: '1',
    date: '2024-01-16',
    riskName: 'Supplier A - Payment Delay',
    previousStatus: 'high',
    currentStatus: 'critical',
    previousScore: 75,
    currentScore: 92,
    description: 'Payment delay escalated due to banking issues'
  },
  {
    id: '2',
    date: '2024-01-15',
    riskName: 'Port D - Weather Delays',
    previousStatus: 'medium',
    currentStatus: 'low',
    previousScore: 55,
    currentScore: 25,
    description: 'Weather conditions improved, operations resuming'
  },
  {
    id: '3',
    date: '2024-01-15',
    riskName: 'Region B - Geopolitical Tensions',
    previousStatus: 'high',
    currentStatus: 'high',
    previousScore: 80,
    currentScore: 78,
    description: 'Minor improvement in diplomatic relations'
  },
  {
    id: '4',
    date: '2024-01-14',
    riskName: 'Supplier C - Quality Issues',
    previousStatus: 'low',
    currentStatus: 'medium',
    previousScore: 30,
    currentScore: 55,
    description: 'New quality defects identified in recent shipment'
  },
  {
    id: '5',
    date: '2024-01-14',
    riskName: 'Supplier E - Compliance Alert',
    previousStatus: 'medium',
    currentStatus: 'high',
    previousScore: 60,
    currentScore: 82,
    description: 'Regulatory compliance issues discovered'
  },
  {
    id: '6',
    date: '2024-01-13',
    riskName: 'Region F - Market Volatility',
    previousStatus: 'medium',
    currentStatus: 'medium',
    previousScore: 50,
    currentScore: 48,
    description: 'Market conditions remain unstable'
  }
];

const getStatusColor = (status: TimelineEvent['currentStatus']) => {
  switch (status) {
    case 'critical':
      return 'bg-red-500';
    case 'high':
      return 'bg-orange-500';
    case 'medium':
      return 'bg-yellow-500';
    case 'low':
      return 'bg-green-500';
  }
};

const getStatusTextColor = (status: TimelineEvent['currentStatus']) => {
  switch (status) {
    case 'critical':
      return 'text-red-500';
    case 'high':
      return 'text-orange-500';
    case 'medium':
      return 'text-yellow-500';
    case 'low':
      return 'text-green-500';
  }
};

const getTrendIcon = (prev: number, current: number) => {
  if (current > prev) {
    return <ArrowUp className="h-4 w-4 text-red-500" />;
  } else if (current < prev) {
    return <ArrowDown className="h-4 w-4 text-green-500" />;
  }
  return <Minus className="h-4 w-4 text-muted-foreground" />;
};

export default function RiskProgressionTimeline({
  events = mockEvents,
  maxEvents = 10
}: RiskProgressionTimelineProps) {
  const [filter, setFilter] = useState<'all' | 'escalated' | 'improved'>('all');

  const filteredEvents = events
    .filter((event) => {
      if (filter === 'escalated') return event.currentScore > event.previousScore;
      if (filter === 'improved') return event.currentScore < event.previousScore;
      return true;
    })
    .slice(0, maxEvents);

  const groupedByDate = filteredEvents.reduce((acc, event) => {
    if (!acc[event.date]) {
      acc[event.date] = [];
    }
    acc[event.date].push(event);
    return acc;
  }, {} as Record<string, TimelineEvent[]>);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All Changes
        </Button>
        <Button
          variant={filter === 'escalated' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('escalated')}
        >
          <ArrowUp className="h-4 w-4 mr-1" />
          Escalated
        </Button>
        <Button
          variant={filter === 'improved' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('improved')}
        >
          <ArrowDown className="h-4 w-4 mr-1" />
          Improved
        </Button>
      </div>

      <div className="relative">
        {/* Timeline vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border" />

        <div className="space-y-6">
          {Object.entries(groupedByDate).map(([date, dateEvents]) => (
            <div key={date}>
              <div className="flex items-center gap-3 mb-4">
                <div className="relative z-10 bg-background px-2">
                  <Badge variant="outline" className="font-semibold">
                    {new Date(date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </Badge>
                </div>
                <div className="flex-1 h-px bg-border" />
              </div>

              <div className="space-y-3">
                {dateEvents.map((event) => (
                  <div key={event.id} className="flex gap-4">
                    {/* Timeline dot */}
                    <div className="relative flex-shrink-0">
                      <div
                        className={`w-4 h-4 rounded-full border-4 border-background ${
                          getStatusColor(event.currentStatus)
                        } mt-1.5`}
                      />
                    </div>

                    {/* Event card */}
                    <Card className="flex-1 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold">{event.riskName}</h4>
                            {getTrendIcon(event.previousScore, event.currentScore)}
                          </div>

                          <p className="text-sm text-muted-foreground mb-3">
                            {event.description}
                          </p>

                          <div className="flex items-center gap-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Previous: </span>
                              <Badge
                                variant="outline"
                                className={`capitalize ${getStatusTextColor(
                                  event.previousStatus
                                )}`}
                              >
                                {event.previousStatus} ({event.previousScore})
                              </Badge>
                            </div>
                            <span className="text-muted-foreground">→</span>
                            <div>
                              <span className="text-muted-foreground">Current: </span>
                              <Badge
                                variant="outline"
                                className={`capitalize ${getStatusTextColor(
                                  event.currentStatus
                                )}`}
                              >
                                {event.currentStatus} ({event.currentScore})
                              </Badge>
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-2xl font-bold">
                            {event.currentScore > event.previousScore ? '+' : ''}
                            {event.currentScore - event.previousScore}
                          </div>
                          <div className="text-xs text-muted-foreground">Score Change</div>
                        </div>
                      </div>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {filteredEvents.length === 0 && (
          <div className="text-center py-12">
            <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No risk changes found for selected filter</p>
          </div>
        )}
      </div>
    </div>
  );
}