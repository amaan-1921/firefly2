// src/app/(dashboard)/impact/page.tsx
'use client';

import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button
} from '@mui/material';
import { useMemo } from 'react';
import { useAlertStore } from '@/store/useAlertStore';
import { useAlerts } from '@/hooks/useAlerts';
import { useImpactData } from '@/hooks/useImpactData';

export default function ImpactPage() {
  const selectedAlert = useAlertStore((s) => s.selectedAlert);
  const { data: alerts = [] } = useAlerts();

  const alert = useMemo(() => {
    if (selectedAlert) return selectedAlert;
    if (!alerts.length) return undefined;
    return alerts[0];
  }, [alerts, selectedAlert]);

  const { data: rows = [] } = useImpactData(alert?.id ?? null);

  const totalRevenueAtRisk = useMemo(
    () => rows.reduce((sum, po) => sum + po.financialImpact, 0),
    [rows]
  );

  const columns: GridColDef[] = [
    { field: 'poNumber', headerName: 'PO #', flex: 0.8, minWidth: 120 },
    { field: 'supplierName', headerName: 'Supplier', flex: 1.2, minWidth: 160 },
    { field: 'item', headerName: 'Item', flex: 1.5, minWidth: 200 },
    {
      field: 'quantity',
      headerName: 'Quantity',
      type: 'number',
      flex: 0.7,
      minWidth: 120
    },
    {
      field: 'dueDate',
      headerName: 'Due Date',
      flex: 0.8,
      minWidth: 130
    },
    {
      field: 'financialImpact',
      headerName: 'Financial Impact',
      flex: 1,
      minWidth: 160,
      valueFormatter: (params) =>
        `$${(params.value as number).toLocaleString()}`,
      renderCell: (params) => (
        <span className="font-semibold text-primary-red">
          ${params.value.toLocaleString()}
        </span>
      )
    }
  ];

  if (!alert) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold text-slate-900">
          Impact Identification
        </h1>
        <p className="text-sm text-slate-500 mt-2">
          No alert selected. Navigate from Alerts to investigate financial
          impact.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 pb-4 border-b border-slate-200 bg-bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Impact Analysis: {alert.title}
            </h1>
            <p className="text-sm text-slate-500">
              Translate a generic port delay into specific dollars at risk.
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400 uppercase mb-1">Alert</p>
            <p className="text-sm font-semibold text-slate-900">
              Critical Alert: Shanghai Port Delay
            </p>
            <p className="text-xs text-slate-500">
              Impact: High ({alert.impactedPoCount} POs affected) · Status:
              Decision Pending
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-slate-50 p-6">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
          {/* Left: Dense Data Grid */}
          <Card className="xl:col-span-3 rounded-xl shadow-sm border border-slate-100">
            <CardHeader
              title={
                <Typography variant="subtitle1" className="text-slate-900">
                  Affected Purchase Orders
                </Typography>
              }
              subheader={
                <span className="text-xs text-slate-400">
                  Dense, sortable grid of POs impacted by this alert.
                </span>
              }
            />
            <CardContent className="h-[480px]">
              <DataGrid
                rows={rows}
                columns={columns}
                getRowId={(row) => row.id}
                disableRowSelectionOnClick
                density="compact"
                pageSizeOptions={[5, 10, 25]}
                initialState={{
                  pagination: { paginationModel: { pageSize: 5, page: 0 } }
                }}
              />
            </CardContent>
          </Card>

          {/* Right: Total Revenue at Risk */}
          <Card className="xl:col-span-1 rounded-xl shadow-sm border border-slate-100">
            <CardHeader
              title={
                <Typography variant="subtitle1" className="text-slate-900">
                  Total Revenue at Risk
                </Typography>
              }
            />
            <CardContent className="space-y-4">
              <div>
                <p className="text-3xl font-bold text-primary-red">
                  ${totalRevenueAtRisk.toLocaleString()}
                </p>
                <p className="text-xs text-slate-500">
                  (Across {rows.length} affected POs)
                </p>
              </div>

              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-primary-red"
                  style={{ width: rows.length ? '72%' : '0%' }}
                />
              </div>
              <p className="text-xs text-slate-500">
                Procurement managers rely on this view to justify decisions
                to leadership.
              </p>

              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => {
                  window.location.href = '/recommendations';
                }}
              >
                View Recommendations
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
