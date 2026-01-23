// src/app/api/alerts/route.ts
import { NextResponse } from 'next/server';
import { faker } from '@faker-js/faker';
import type { Alert, RiskCategory, AlertSeverity } from '@/types/alert';

const severities: AlertSeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const categories: RiskCategory[] = [
  'GEOPOLITICAL',
  'WEATHER',
  'LOGISTICS',
  'SUPPLIER_PERFORMANCE',
  'TARIFF',
  'OTHER'
];

function generateAlert(): Alert {
  const severity = faker.helpers.arrayElement(severities);
  const riskCategory = faker.helpers.arrayElement(categories);
  const impactedPoCount = faker.number.int({ min: 1, max: 20 });
  const estimatedRevenueImpact = faker.number.int({
    min: 100_000,
    max: 5_000_000
  });

  const detectedAt = faker.date.recent({ days: 2 }).toISOString();
  const lastUpdatedAt = faker.date.recent({ days: 1 }).toISOString();

  const [lat, lng] = [
    faker.location.latitude(),
    faker.location.longitude()
  ];

  return {
    id: faker.string.uuid(),
    title: `${faker.location.city()} Port Congestion`,
    description: faker.lorem.sentence(),
    severity,
    riskCategory,
    impactedPoCount,
    estimatedRevenueImpact,
    status:
      severity === 'CRITICAL' || severity === 'HIGH'
        ? 'CRITICAL'
        : 'MONITORING',
    source: 'Logistics API',
    detectedAt,
    lastUpdatedAt,
    relatedPoIds: [],
    location: {
      label: faker.location.city(),
      lat,
      lng,
      countryCode: faker.location.countryCode()
    }
  };
}

export async function GET() {
  // Simple env toggle: if BACKEND_URL exists, you would proxy instead.
  if (process.env.BACKEND_URL) {
    // TODO: proxy to real backend
    // const res = await fetch(`${process.env.BACKEND_URL}/alerts`);
    // const data = await res.json();
    // return NextResponse.json(data);
  }

  const alerts: Alert[] = faker.helpers.multiple(generateAlert, {
    count: 8
  });

  return NextResponse.json(alerts);
}
