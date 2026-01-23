export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type RiskCategory =
  | 'GEOPOLITICAL'
  | 'WEATHER'
  | 'LOGISTICS'
  | 'SUPPLIER_PERFORMANCE'
  | 'TARIFF'
  | 'OTHER';

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: AlertSeverity;
  riskCategory: RiskCategory;
  impactedPoCount: number;
  estimatedRevenueImpact: number;
  status: 'CRITICAL' | 'MONITORING' | 'RESOLVED' | 'DECISION_PENDING';
  source: string;
  detectedAt: string;
  lastUpdatedAt: string;
  relatedPoIds: string[];
  location?: {
    label: string;
    lat: number;
    lng: number;
    countryCode?: string;
  };
}
