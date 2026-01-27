// src/app/(dashboard)/settings/page.tsx
'use client';

import {
  Card,
  CardContent,
  CardHeader,
  FormControlLabel,
  Switch,
  Typography,
  Slider
} from '@mui/material';
import { useState } from 'react';

export default function SettingsPage() {
  const [autoStartMonitoring, setAutoStartMonitoring] = useState(true);
  const [defaultThreshold, setDefaultThreshold] = useState(500000);
  const [pollInterval, setPollInterval] = useState(60);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-800">Settings</h1>
        <p className="text-sm text-slate-500">
          Configure default monitoring templates and safety constraints.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader
            title={
              <Typography variant="subtitle1">
                Monitoring Templates
              </Typography>
            }
            subheader={
              <span className="text-xs text-slate-400">
                Defaults used when starting new monitoring sessions.
              </span>
            }
          />
          <CardContent className="space-y-4">
            <FormControlLabel
              control={
                <Switch
                  checked={autoStartMonitoring}
                  onChange={(e) => setAutoStartMonitoring(e.target.checked)}
                />
              }
              label={
                <span className="text-sm text-slate-600">
                  Auto-start monitoring with default filters
                </span>
              }
            />
            <div>
              <p className="text-xs font-semibold text-slate-500 mb-2">
                Default Impact Threshold
              </p>
              <Slider
                min={0}
                max={1000000}
                step={50000}
                value={defaultThreshold}
                onChange={(_, v) => setDefaultThreshold(v as number)}
                valueLabelDisplay="auto"
              />
              <p className="text-xs text-slate-400 mt-1">
                New sessions start at ${defaultThreshold.toLocaleString()} impact
                threshold.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            title={
              <Typography variant="subtitle1">
                Safety & Polling
              </Typography>
            }
            subheader={
              <span className="text-xs text-slate-400">
                Align system behavior with Safety Progression.
              </span>
            }
          />
          <CardContent className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-slate-500 mb-2">
                Alert Polling Interval (seconds)
              </p>
              <Slider
                min={15}
                max={300}
                step={15}
                value={pollInterval}
                onChange={(_, v) => setPollInterval(v as number)}
                valueLabelDisplay="auto"
              />
              <p className="text-xs text-slate-400 mt-1">
                Current interval {pollInterval}s. Align this with TanStack Query
                config in production.
              </p>
            </div>
            <FormControlLabel
              control={<Switch defaultChecked />}
              label={
                <span className="text-sm text-slate-600">
                  Require manual approval before automation
                </span>
              }
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
