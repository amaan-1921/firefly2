'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface RiskItem {
  id: string;
  name: string;
  category: string;
  status: 'critical' | 'high' | 'medium' | 'low';
  score: number;
  lastUpdated: string;
}

interface TrafficLightViewProps {
  risks?: RiskItem[];
  view?: 'grid' | 'list';
  onRiskClick?: (risk: RiskItem) => void;
}

const mockRisks: RiskItem[] = [
  {
    id: '1',
    name: 'Supplier A - Payment Delay',
    category: 'Financial',
    status: 'critical',
    score: 92,
    lastUpdated: '2024-01-15'
  },
  {
    id: '2',
    name: 'Region B - Geopolitical Tensions',
    category: 'Geopolitical',
    status: 'high',
    score: 78,
    lastUpdated: '2024-01-14'
  },
  {
    id: '3',
    name: 'Supplier C - Quality Issues',
    category: 'Operational',
    status: 'medium',
    score: 55,
    lastUpdated: '2024-01-15'
  },
  {
    id: '4',
    name: 'Port D - Weather Delays',
    category: 'Logistics',
    status: 'low',
    score: 25,
    lastUpdated: '2024-01-16'
  },
  {
    id: '5',
    name: 'Supplier E - Compliance Alert',
    category: 'Regulatory',
    status: 'high',
    score: 82,
    lastUpdated: '2024-01-15'
  },
  {
    id: '6',
    name: 'Region F - Market Volatility',
    category: 'Financial',
    status: 'medium',
    score: 48,
    lastUpdated: '2024-01-14'
  }
];

const getStatusColor = (status: RiskItem['status']) => {
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

const getStatusIcon = (status: RiskItem['status']) => {
  switch (status) {
    case 'critical':
      return <XCircle className="h-5 w-5" />;
    case 'high':
      return <AlertTriangle className="h-5 w-5" />;
    case 'medium':
      return <AlertCircle className="h-5 w-5" />;
    case 'low':
      return <CheckCircle className="h-5 w-5" />;
  }
};

const getStatusBadge = (status: RiskItem['status']) => {
  const variants = {
    critical: 'destructive',
    high: 'destructive',
    medium: 'default',
    low: 'secondary'
  };
  
  return (
    <Badge variant={variants[status] as any} className="capitalize">
      {status}
    </Badge>
  );
};

export default function TrafficLightView({
  risks = mockRisks,
  view = 'grid',
  onRiskClick
}: TrafficLightViewProps) {
  const groupedByStatus = risks.reduce((acc, risk) => {
    if (!acc[risk.status]) {
      acc[risk.status] = [];
    }
    acc[risk.status].push(risk);
    return acc;
  }, {} as Record<string, RiskItem[]>);

  if (view === 'grid') {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {(['critical', 'high', 'medium', 'low'] as const).map((status) => (
            <Card
              key={status}
              className="p-4 border-l-4"
              style={{
                borderLeftColor:
                  status === 'critical'
                    ? '#ef4444'
                    : status === 'high'
                    ? '#f97316'
                    : status === 'medium'
                    ? '#eab308'
                    : '#22c55e'
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`${getStatusColor(status)} p-2 rounded-full text-white`}>
                    {getStatusIcon(status)}
                  </div>
                  <h3 className="font-semibold capitalize">{status} Risk</h3>
                </div>
                <Badge variant="outline" className="text-lg font-bold">
                  {groupedByStatus[status]?.length || 0}
                </Badge>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {groupedByStatus[status]?.map((risk) => (
                  <div
                    key={risk.id}
                    onClick={() => onRiskClick?.(risk)}
                    className="p-2 bg-secondary/50 rounded hover:bg-secondary cursor-pointer transition-colors"
                  >
                    <div className="font-medium text-sm truncate">{risk.name}</div>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-xs text-muted-foreground">
                        {risk.category}
                      </span>
                      <span className="text-xs font-semibold">
                        Score: {risk.score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // List view
  return (
    <div className="space-y-3">
      {risks
        .sort((a, b) => b.score - a.score)
        .map((risk) => (
          <Card
            key={risk.id}
            onClick={() => onRiskClick?.(risk)}
            className="p-4 cursor-pointer hover:shadow-md transition-shadow border-l-4"
            style={{
              borderLeftColor:
                risk.status === 'critical'
                  ? '#ef4444'
                  : risk.status === 'high'
                  ? '#f97316'
                  : risk.status === 'medium'
                  ? '#eab308'
                  : '#22c55e'
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className={`${getStatusColor(risk.status)} p-2 rounded-full text-white`}>
                  {getStatusIcon(risk.status)}
                </div>
                <div className="flex-1">
                  <div className="font-semibold">{risk.name}</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {risk.category} • Updated {risk.lastUpdated}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-2xl font-bold">{risk.score}</div>
                  <div className="text-xs text-muted-foreground">Risk Score</div>
                </div>
                {getStatusBadge(risk.status)}
              </div>
            </div>
          </Card>
        ))}
    </div>
  );
}