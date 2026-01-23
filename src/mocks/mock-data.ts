// src/mocks/mock-data.ts
import { Alert } from '@/types/alert';
import { PO } from '@/types/po';
import { Supplier } from '@/types/supplier';


export const mockAlerts: Alert[] = [
  {
    id: 'alert-shanghai-port',
    title: 'Port Congestion - Shanghai',
    description: 'Critical delay at Shanghai Port impacting multiple POs.',
    severity: 'CRITICAL',
    riskCategory: 'LOGISTICS',
    impactedPoCount: 5,
    estimatedRevenueImpact: 5970000,
    status: 'CRITICAL',
    source: 'Logistics API',
    detectedAt: new Date().toISOString(),
    lastUpdatedAt: new Date().toISOString(),
    relatedPoIds: ['PO-001234', 'PO-001235', 'PO-001236', 'PO-001237', 'PO-001238'],
    location: {
      label: 'Shanghai Port',
      lat: 31.2304,
      lng: 121.4737,
      countryCode: 'CN'
    }
  }
];


export const mockSuppliers: Supplier[] = [
  {
    id: 'supplier-techcomponents',
    name: 'TechComponents Inc.',
    location: 'Shanghai, China',
    performanceScore: 99,
    status: 'NORMAL',
    isInternal: false,
    leadTimeDays: 20,
    logisticsRiskScore: 0.4,
    activePoIds: ['PO-001234', 'PO-001237'],
    relatedAlertIds: ['alert-shanghai-port']
  }
];


export const mockPOs: PO[] = [
  {
    id: 'po-001234',
    poNumber: 'PO-001234',
    supplierId: 'supplier-techcomponents',
    supplierName: 'TechComponents Inc.',
    item: 'Semiconductor Chips',
    quantity: 50000,
    dueDate: '2025-11-15',
    currency: 'USD',
    financialImpact: 1200000,
    status: 'DELAYED',
    alertIds: ['alert-shanghai-port']
  }
];