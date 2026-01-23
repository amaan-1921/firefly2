'use client';

import {
  AlertTriangle,
  Package,
  DollarSign,
  TrendingDown,
  Clock,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAlerts } from '@/hooks/useAlerts';
import { useMemo } from 'react';

export default function DashboardPage() {
  const { data: alerts = [], isLoading } = useAlerts();

  const { criticalCount, warningCount, safeCount, totalImpact } = useMemo(() => {
    let criticalCount = 0;
    let warningCount = 0;
    let safeCount = 0;
    let totalImpact = 0;

    alerts.forEach((a) => {
      totalImpact += a.estimatedRevenueImpact;
      if (a.severity === 'CRITICAL' || a.severity === 'HIGH') {
        criticalCount += 1;
      } else if (a.severity === 'MEDIUM') {
        warningCount += 1;
      } else {
        safeCount += 1;
      }
    });

    return { criticalCount, warningCount, safeCount, totalImpact };
  }, [alerts]);

  const kpiCards = [
    {
      title: 'Active Alerts',
      icon: AlertTriangle,
      counts: {
        critical: criticalCount,
        warning: warningCount,
        safe: safeCount,
      },
    },
    {
      title: 'Suppliers at Risk',
      value: alerts.length ? '23' : '0',
      icon: Package,
      trend: alerts.length ? '+3 from last week' : 'No new suppliers added',
      color: '#E57373',
    },
    {
      title: 'Open POs Impacted',
      value: alerts.length ? '187' : '0',
      icon: TrendingDown,
      trend: alerts.length ? 'Across 23 suppliers' : 'No POs impacted',
      color: '#D84315',
    },
    {
      title: 'Estimated Revenue Impact',
      value:
        totalImpact > 0
          ? `$${(totalImpact * 0.9).toLocaleString()} – $${(
              totalImpact * 1.1
            ).toLocaleString()}`
          : '$0 – $0',
      icon: DollarSign,
      trend: 'Next 30 days',
      color: '#D84315',
    },
  ];

  const criticalAlerts = [
    {
      supplier: 'TechCorp Industries',
      reason: 'Port congestion – Shanghai',
      poCount: 14,
      severity: 'critical',
    },
    {
      supplier: 'GlobalComponents Ltd',
      reason: 'Geopolitical tensions – Taiwan Strait',
      poCount: 22,
      severity: 'critical',
    },
    {
      supplier: 'MicroElectronics SA',
      reason: 'Severe weather – Hurricane warning',
      poCount: 8,
      severity: 'warning',
    },
    {
      supplier: 'Pacific Suppliers Co',
      reason: 'Labor strike – Port workers',
      poCount: 18,
      severity: 'critical',
    },
    {
      supplier: 'Nordic Materials AB',
      reason: 'Factory fire – Production halted',
      poCount: 6,
      severity: 'warning',
    },
  ];

  const recentActivity = [
    {
      timestamp: '2 minutes ago',
      event: 'RFQ auto-sent to 3 alternative suppliers for PO-28473',
      type: 'automated',
    },
    {
      timestamp: '14 minutes ago',
      event: 'New geopolitical alert: Trade restrictions announced',
      type: 'alert',
    },
    {
      timestamp: '23 minutes ago',
      event: 'Supplier risk score updated: TechCorp Industries (High → Critical)',
      type: 'update',
    },
    {
      timestamp: '1 hour ago',
      event: 'Impact analysis completed for 14 affected POs',
      type: 'analysis',
    },
    {
      timestamp: '2 hours ago',
      event:
        'Weather monitoring detected hurricane formation – Gulf Coast corridor',
      type: 'alert',
    },
  ];

  const riskZones = [
    { region: 'Shanghai Port', lat: 31.2, lon: 121.5, intensity: 'critical' },
    { region: 'Taiwan Strait', lat: 24.5, lon: 120.5, intensity: 'critical' },
    { region: 'Gulf Coast', lat: 29.0, lon: -90.0, intensity: 'warning' },
    { region: 'Suez Canal', lat: 30.0, lon: 32.5, intensity: 'warning' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 pb-4 border-b border-slate-200 bg-bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Dashboard
            </h1>
            <p className="text-sm text-slate-500">
              Command center for global supply chain risk.
            </p>
          </div>
          {isLoading && (
            <span className="text-xs text-slate-400">
              Polling alerts every 60s…
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-slate-50 p-6 space-y-6">
        {/* KPI row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpiCards.map((kpi, i) => {
            const Icon = kpi.icon;
            return (
              <Card key={i} className="shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">
                        {kpi.title}
                      </p>
                      {'counts' in kpi && kpi.counts ? (
                        <div className="flex gap-4 mt-3">
                          <div className="text-center">
                            <div className="text-2xl font-semibold text-[#D84315]">
                              {kpi.counts.critical}
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              Critical
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-semibold text-[#E57373]">
                              {kpi.counts.warning}
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              Warning
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-semibold text-[#81C784]">
                              {kpi.counts.safe}
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              Safe
                            </div>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div
                            className="text-2xl font-semibold"
                            style={{ color: (kpi as any).color }}
                          >
                            {(kpi as any).value}
                          </div>
                          {(kpi as any).trend && (
                            <p className="text-xs text-slate-500 mt-2">
                              {(kpi as any).trend}
                            </p>
                          )}
                        </>
                      )}
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50">
                      <Icon
                        size={22}
                        strokeWidth={1.5}
                        className="text-slate-500"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Middle row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Critical Alerts */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>Top Critical Alerts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {criticalAlerts.map((alert, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border-l-4 ${
                    alert.severity === 'critical'
                      ? 'border-[#D84315] bg-[#D84315]/5 animate-pulse'
                      : 'border-[#E57373] bg-[#E57373]/5'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <AlertTriangle
                          size={16}
                          strokeWidth={1.5}
                          className={
                            alert.severity === 'critical'
                              ? 'text-[#D84315]'
                              : 'text-[#E57373]'
                          }
                        />
                        <span className="text-sm font-medium text-slate-900">
                          {alert.supplier}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        {alert.reason}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold text-slate-900">
                        {alert.poCount} POs
                      </div>
                      <div className="text-[11px] text-slate-500">
                        affected
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Global Risk Snapshot */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>Global Risk Snapshot</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative h-80 bg-gradient-to-b from-blue-50 to-white rounded-lg overflow-hidden">
                <svg
                  viewBox="0 0 800 400"
                  className="w-full h-full"
                  style={{
                    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
                  }}
                >
                  <rect width="800" height="400" fill="#E3F2FD" />
                  <g fill="#CFD8DC" stroke="#90A4AE" strokeWidth="1">
                    <path d="M 100,80 L 80,120 L 90,160 L 120,180 L 160,170 L 200,140 L 210,100 L 190,70 L 150,60 Z" />
                    <path d="M 150,220 L 140,260 L 160,320 L 180,310 L 170,250 Z" />
                    <path d="M 380,80 L 360,100 L 370,130 L 410,120 L 430,90 Z" />
                    <path d="M 380,160 L 360,200 L 380,280 L 430,270 L 440,190 L 420,160 Z" />
                    <path d="M 480,60 L 460,100 L 480,140 L 550,150 L 620,130 L 650,100 L 630,70 L 580,50 Z" />
                    <path d="M 600,280 L 580,300 L 600,320 L 640,310 L 650,290 Z" />
                  </g>
                  {riskZones.map((zone, i) => {
                    const x = ((zone.lon + 180) * 800) / 360;
                    const y = ((90 - zone.lat) * 400) / 180;
                    const color =
                      zone.intensity === 'critical' ? '#D84315' : '#E57373';
                    return (
                      <g key={i}>
                        <circle
                          cx={x}
                          cy={y}
                          r="20"
                          fill={color}
                          opacity="0.2"
                        >
                          <animate
                            attributeName="r"
                            values="20;30;20"
                            dur="2s"
                            repeatCount="indefinite"
                          />
                        </circle>
                        <circle
                          cx={x}
                          cy={y}
                          r="8"
                          fill={color}
                          opacity="0.8"
                        />
                        <circle cx={x} cy={y} r="4" fill="white" />
                      </g>
                    );
                  })}
                </svg>

                <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm p-3 rounded-lg shadow-sm flex gap-4 text-[11px] text-slate-700">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#D84315]" />
                    Critical risk
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#E57373]" />
                    Warning
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentActivity.map((a, i) => (
              <div
                key={i}
                className="flex items-start gap-4 pb-4 border-b border-slate-100 last:border-0"
              >
                <div className="mt-1">
                  <Clock
                    size={16}
                    strokeWidth={1.5}
                    className="text-slate-400"
                  />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-slate-900">{a.event}</p>
                  <p className="text-xs text-slate-500 mt-1">{a.timestamp}</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    a.type === 'alert'
                      ? 'border-[#E57373] text-[#D84315] bg-[#E57373]/5'
                      : a.type === 'automated'
                      ? 'border-[#81C784] text-green-700 bg-[#81C784]/5'
                      : 'border-slate-200 text-slate-600'
                  }
                >
                  {a.type}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
