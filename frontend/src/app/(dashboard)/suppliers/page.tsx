// src/app/(dashboard)/suppliers/page.tsx
'use client';

import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Card, CardContent, CardHeader, Typography } from '@mui/material';
import { faker } from '@faker-js/faker';
import type { Supplier } from '@/types/supplier';

function generateSuppliers(count = 20): Supplier[] {
  return Array.from({ length: count }).map(() => {
    const performanceScore = faker.number.int({ min: 80, max: 100 });
    const status: Supplier['status'] =
      performanceScore > 95
        ? 'NORMAL'
        : performanceScore > 88
        ? 'AT_RISK'
        : 'CRITICAL';

    return {
      id: faker.string.uuid(),
      name: faker.company.name(),
      location: `${faker.location.city()}, ${faker.location.country()}`,
      performanceScore,
      status,
      isInternal: faker.datatype.boolean(),
      leadTimeDays: faker.number.int({ min: 5, max: 25 }),
      logisticsRiskScore: Math.round(Math.random() * 100) / 100,
      activePoIds: [],
      relatedAlertIds: []
    };
  });
}

const suppliers = generateSuppliers();

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Supplier', flex: 1.5, minWidth: 180 },
  { field: 'location', headerName: 'Location', flex: 1.5, minWidth: 180 },
  {
    field: 'performanceScore',
    headerName: 'Performance',
    flex: 0.7,
    minWidth: 120
  },
  {
    field: 'status',
    headerName: 'Status',
    flex: 0.6,
    minWidth: 110
  },
  {
    field: 'leadTimeDays',
    headerName: 'Lead Time (days)',
    flex: 0.8,
    minWidth: 140
  }
];

export default function SuppliersPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-800">Suppliers</h1>
        <p className="text-sm text-slate-500">
          Overview of supplier performance and risk posture.
        </p>
      </div>

      <Card>
        <CardHeader
          title={
            <Typography variant="subtitle1">
              Supplier Performance Grid
            </Typography>
          }
          subheader={
            <span className="text-xs text-slate-400">
              Use this view to identify suppliers trending towards risk.
            </span>
          }
        />
        <CardContent className="h-[520px]">
          <DataGrid
            rows={suppliers}
            columns={columns}
            getRowId={(row) => row.id}
            density="compact"
            pageSizeOptions={[10, 25, 50]}
            initialState={{
              pagination: { paginationModel: { pageSize: 10, page: 0 } }
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
