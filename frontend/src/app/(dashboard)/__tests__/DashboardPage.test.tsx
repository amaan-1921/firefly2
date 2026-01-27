// src/app/(dashboard)/__tests__/DashboardPage.test.tsx
import { render, screen } from '@testing-library/react';
import DashboardPage from '../dashboard/page';
import { createWrapper } from '@/test/utils';

// mock useAlerts
jest.mock('@/hooks/useAlerts', () => ({
  useAlerts: () => ({
    data: [
      {
        id: '1',
        title: 'Test Alert',
        description: 'desc',
        severity: 'CRITICAL',
        riskCategory: 'LOGISTICS',
        impactedPoCount: 3,
        estimatedRevenueImpact: 1000000,
        status: 'CRITICAL',
        source: 'Logistics API',
        detectedAt: new Date().toISOString(),
        lastUpdatedAt: new Date().toISOString(),
        relatedPoIds: [],
        location: { label: 'Test', lat: 0, lng: 0 }
      }
    ],
    isLoading: false
  })
}));

test('renders KPI cards', () => {
  render(<DashboardPage />, { wrapper: createWrapper() });
  expect(screen.getByText(/Control Tower/i)).toBeInTheDocument();
  expect(screen.getByText(/Active Alerts/i)).toBeInTheDocument();
});
