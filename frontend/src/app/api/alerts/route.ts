// src/app/api/alerts/route.ts
import { NextResponse } from 'next/server';
import type { Alert } from '@/types/alert';

// Map priority to severity
function priorityToSeverity(priority: string): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  switch (priority) {
    case 'P1':
      return 'CRITICAL';
    case 'P2':
      return 'HIGH';
    case 'P3':
      return 'MEDIUM';
    default:
      return 'LOW';
  }
}

// Map relatedSignals to riskCategory
function signalToCategory(signals: string[]): string {
  if (!signals || signals.length === 0) return 'OTHER';
  
  const signal = signals[0];
  if (signal.includes('NEWS')) return 'GEOPOLITICAL';
  if (signal.includes('WEATHER')) return 'WEATHER';
  if (signal.includes('LOGISTICS')) return 'LOGISTICS';
  if (signal.includes('SUPPLIER')) return 'SUPPLIER_PERFORMANCE';
  if (signal.includes('TARIFF')) return 'TARIFF';
  return 'OTHER';
}

export async function GET() {
  try {
    // Call FastAPI backend
    const res = await fetch('http://localhost:8000/alerts/run-from-jsonl', {
      method: 'GET',
    });

    if (!res.ok) {
      throw new Error(`FastAPI returned ${res.status}`);
    }

    const rawAlerts = await res.json();

    // Transform FastAPI response to match frontend Alert type
    const transformedAlerts: Alert[] = rawAlerts.map((alert: any) => ({
      id: alert.alertId,
      title: alert.title,
      description: alert.summary,
      severity: priorityToSeverity(alert.priority),
      riskCategory: signalToCategory(alert.relatedSignals),
      impactedPoCount: 0, // You may need to derive this from the API response
      estimatedRevenueImpact: 0, // You may need to derive this from the API response
      status: 'MONITORING',
      source: 'News Intelligence',
      detectedAt: alert.createdAt,
      lastUpdatedAt: alert.createdAt,
      relatedPoIds: [],
      // Optional: add location if available in your data
    }));

    return NextResponse.json(transformedAlerts);
  } catch (error) {
    console.error('Error fetching alerts from FastAPI:', error);
    return NextResponse.json(
      { error: 'Failed to fetch alerts' },
      { status: 500 }
    );
  }
}
