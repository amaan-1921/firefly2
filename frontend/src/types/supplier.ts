export type SupplierStatus = 'NORMAL' | 'AT_RISK' | 'CRITICAL';

export interface Supplier {
  id: string;
  name: string;
  location: string;
  performanceScore: number;
  status: SupplierStatus;
  isInternal: boolean;
  leadTimeDays?: number;
  logisticsRiskScore?: number;
  activePoIds: string[];
  relatedAlertIds: string[];
}
