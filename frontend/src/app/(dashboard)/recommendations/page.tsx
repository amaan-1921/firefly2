// src/app/(dashboard)/recommendations/page.tsx
'use client';

import { useMemo, useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
// import { useAlertStore } from '@/store/useAlertStore';
import { useAlerts } from '@/hooks/useAlerts';

type RecommendationOptionType =
  | 'INTERNAL_FAST'
  | 'EXTERNAL_A'
  | 'EXTERNAL_B';

interface RecommendationOption {
  id: RecommendationOptionType;
  label: string;
  type: 'INTERNAL' | 'EXTERNAL';
  badge: 'Top Pick' | 'Fastest' | 'Cost Efficient';
  description: string;
  leadTimeDays: number;
  daysOfStockRemaining: number;
  costDelta: number;
  riskScore: 'LOW' | 'MEDIUM' | 'HIGH';
}

export default function RecommendationsPage() {
const selectedAlertId: string | null = null; // Not using selected alert for recommendations
  // const resetAlert = useAlertStore((s) => s.reset); // Not using reset for recommendations
  const { data: alerts = [], isLoading, isError } = useAlerts();

  const alert = useMemo(() => {
    if (!alerts.length) return undefined;
    if (selectedAlertId) {
      const found = alerts.find((a) => a.id === selectedAlertId);
      if (found) return found;
    }
    return alerts[0];
  }, [alerts, selectedAlertId]);

  const [showSuccess, setShowSuccess] = useState(false);
  const [selectedOption, setSelectedOption] =
    useState<RecommendationOptionType>('INTERNAL_FAST');

  const impactedPos = useMemo(
    () => alerts.filter((a) => a.id === alert?.id).flatMap((a) => a.relatedPoIds),
    [alerts, alert?.id]
  );
  const totalQty = impactedPos.length; // Simplified

  const options: RecommendationOption[] = [
    {
      id: 'INTERNAL_FAST',
      label: 'Internal Inventory Transfer',
      type: 'INTERNAL',
      badge: 'Top Pick',
      description:
        'Rebalance stock from Vietnam factory to cover delayed shipments.',
      leadTimeDays: 5,
      daysOfStockRemaining: 18,
      costDelta: 2,
      riskScore: 'LOW'
    },
    {
      id: 'EXTERNAL_A',
      label: 'External Supplier A – Global Tech Ltd.',
      type: 'EXTERNAL',
      badge: 'Fastest',
      description:
        'Place an emergency PO with pre-qualified external supplier.',
      leadTimeDays: 15,
      daysOfStockRemaining: 18,
      costDelta: -5,
      riskScore: 'MEDIUM'
    },
    {
      id: 'EXTERNAL_B',
      label: 'External Supplier B – Apex Components',
      type: 'EXTERNAL',
      badge: 'Cost Efficient',
      description:
        'Source from lower-cost vendor with slightly longer lead time.',
      leadTimeDays: 20,
      daysOfStockRemaining: 18,
      costDelta: -8,
      riskScore: 'MEDIUM'
    }
  ];

  const selected = options.find((o) => o.id === selectedOption)!;

  const handleApprove = () => {
    // In production: use a React Query mutation to POST to /api/recommendations/execute
    // For now: simulate success
    setShowSuccess(true);
  };

  const handleCloseSuccess = () => {
    setShowSuccess(false);
    // Auto-resolve: clear selection and return to dashboard
//     resetAlert();
    window.location.href = '/dashboard';
  };

  if (!alert) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold text-slate-800">
          Recommendation Engine
        </h1>
        <p className="text-sm text-slate-500 mt-2">
          No alert selected. Navigate from Impact to see recommendations.
        </p>
        {isError && (
          <p className="text-xs text-primary-red mt-2">
            Failed to load alerts.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">
            Recommendation Engine
          </h1>
          <p className="text-sm text-slate-500">
            Three pre-vetted options to resolve the alert without analysis
            paralysis.
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-400 uppercase mb-1">Alert</p>
          <p className="text-sm font-semibold text-slate-800">{alert.title}</p>
          <p className="text-xs text-slate-500">
            {alert.impactedPoCount} POs · {totalQty} units at risk.
          </p>
        </div>
      </div>

      {isLoading && (
        <p className="text-xs text-slate-400">Loading recommendations…</p>
      )}
      {isError && (
        <p className="text-xs text-primary-red">Failed to load alert data.</p>
      )}

      {!isLoading && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Options (Hick's law: exactly 3) */}
          <Card className="xl:col-span-2">
            <CardHeader
              title={
                <Typography variant="subtitle1">
                  Choose a mitigation strategy
                </Typography>
              }
              subheader={
                <span className="text-xs text-slate-400">
                  Internal options are safer; external options may offer better
                  cost or speed but require qualification.
                </span>
              }
            />
            <CardContent>
              <RadioGroup
                value={selectedOption}
                onChange={(e) =>
                  setSelectedOption(
                    e.target.value as RecommendationOptionType
                  )
                }
                className="space-y-3"
              >
                {options.map((option) => (
                  <Card
                    key={option.id}
                    className={`border ${
                      option.id === selectedOption
                        ? 'border-primary-red shadow-md'
                        : 'border-slate-200'
                    }`}
                  >
                    <CardContent className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <FormControlLabel
                          value={option.id}
                          control={<Radio size="small" />}
                          label=""
                        />
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-semibold text-slate-800">
                              {option.label}
                            </p>
                            <Chip
                              size="small"
                              label={option.badge}
                              color={
                                option.type === 'INTERNAL'
                                  ? 'success'
                                  : 'warning'
                              }
                            />
                          </div>
                          <p className="text-xs text-slate-500 mt-1">
                            {option.description}
                          </p>
                          <div className="flex flex-wrap gap-3 mt-2 text-xs text-slate-500">
                            <span>
                              Lead time{' '}
                              <span className="font-semibold">
                                {option.leadTimeDays} days
                              </span>
                            </span>
                            <span>
                              Days of stock remaining{' '}
                              <span className="font-semibold">
                                {option.daysOfStockRemaining} days
                              </span>
                            </span>
                            <span>
                              Cost difference{' '}
                              <span
                                className={`font-semibold ${
                                  option.costDelta >= 0
                                    ? 'text-brand-terracotta'
                                    : 'text-safe-green'
                                }`}
                              >
                                {option.costDelta > 0 ? '+' : ''}
                                {option.costDelta}%
                              </span>
                            </span>
                            <span>
                              Risk score{' '}
                              <span className="font-semibold">
                                {option.riskScore}
                              </span>
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>

          {/* Inventory Buffer Visual + Affected lines */}
          <Card className="xl:col-span-1">
            <CardHeader
              title={
                <Typography variant="subtitle1">
                  Inventory Buffer Visual
                </Typography>
              }
              subheader={
                <span className="text-xs text-slate-400">
                  Comparing days of stock remaining vs new lead time.
                </span>
              }
            />
            <CardContent className="space-y-4">
              {/* Simple bar comparison */}
              <div className="space-y-2">
                <p className="text-xs text-slate-500">
                  Days of stock remaining
                </p>
                <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full bg-safe-green"
                    style={{
                      width: `${Math.min(
                        (selected.daysOfStockRemaining / 30) * 100,
                        100
                      )}%`
                    }}
                  />
                </div>
                <p className="text-xs text-slate-500">
                  New lead time {selected.leadTimeDays} days
                </p>
                <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full bg-brand-terracotta"
                    style={{
                      width: `${Math.min(
                        (selected.leadTimeDays / 30) * 100,
                        100
                      )}%`
                    }}
                  />
                </div>
              </div>

              {/* Affected production lines */}
              <div className="pt-2 border-t border-slate-100 space-y-2">
                <p className="text-xs font-semibold text-slate-600">
                  Affected Production Lines
                </p>
                <ul className="space-y-1 text-xs text-slate-500">
                  <li>Line A – Consumer Electronics Assembly</li>
                  <li>Line B – Enterprise Server Boards</li>
                  <li>Line C – Battery Pack Integration</li>
                </ul>
              </div>

              <Button
                variant="contained"
                color={selected.type === 'INTERNAL' ? 'success' : 'warning'}
                fullWidth
                className="mt-2"
                onClick={handleApprove}
              >
                Approve & Execute
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Automation Success Modal (Frame 6) */}
      <Dialog open={showSuccess} onClose={handleCloseSuccess} maxWidth="sm">
        <DialogTitle>RFQ Sent Successfully</DialogTitle>
        <DialogContent>
          <Typography variant="body2" className="text-slate-600">
            <strong>{selected.label}</strong> has been approved and executed.
            <br />
            <br />
            The alert will no longer appear as critical in your dashboard.
            Previously red cards will now be resolved or grayed out.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSuccess} variant="contained">
            Return to Dashboard
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
