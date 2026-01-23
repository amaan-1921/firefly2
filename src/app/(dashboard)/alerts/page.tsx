// src/app/(dashboard)/alerts/page.tsx
'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAlerts } from '@/hooks/useAlerts';

export default function AlertsPage() {
  const { data: alerts = [], isLoading } = useAlerts();
  const [filter, setFilter] =
    useState<'all' | 'CRITICAL' | 'MEDIUM' | 'LOW'>('all');

  const filteredAlerts = alerts.filter(
    (alert) => filter === 'all' || alert.severity === filter,
  );

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'destructive';
      case 'MEDIUM':
        return 'secondary';
      case 'LOW':
        return 'outline';
      default:
        return 'outline';
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center">Loading monitoring signals...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Monitoring</h1>
        <div className="flex gap-2">
          {(['all', 'CRITICAL', 'MEDIUM', 'LOW'] as const).map((severity) => (
            <Button
              key={severity}
              variant={filter === severity ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(severity)}
            >
              {severity === 'all' ? 'All' : severity}
            </Button>
          ))}
        </div>
      </div>

      <Card className="overflow-hidden">
        <div className="border-b px-4 py-3 text-sm font-semibold">
          Detected Monitoring Signals
        </div>
        {filteredAlerts.length === 0 ? (
          <div className="p-6 text-center text-sm text-muted-foreground">
            No monitoring signals found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full border-t text-sm">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold">
                    Alert ID
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Title
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Risk Category
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Location
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Impact
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Status
                  </th>
                  <th className="px-4 py-2 text-left font-semibold">
                    Severity
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredAlerts.map((alert) => (
                  <tr key={alert.id} className="border-t">
                    <td className="px-4 py-2">{alert.id}</td>
                    <td className="px-4 py-2">{alert.title}</td>
                    <td className="px-4 py-2">{alert.riskCategory.replace('_', ' ')}</td>
                    <td className="px-4 py-2">
                      {alert.location?.label ?? '-'}
                    </td>
                    <td className="px-4 py-2">
                      ${alert.estimatedRevenueImpact.toLocaleString()}
                    </td>
                    <td className="px-4 py-2">{alert.status}</td>
                    <td className="px-4 py-2">
                      <Badge variant={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="border-t px-4 py-2 text-xs text-muted-foreground">
              Showing {filteredAlerts.length} signals
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
