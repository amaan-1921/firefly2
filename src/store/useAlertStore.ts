import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Alert } from '@/types/alert';

interface MonitoringConfig {
  riskCategory: string;
  impactThreshold: number;
  frequency: string;
  isActive: boolean;
}

interface Recommendation {
  id: string;
  type: 'internal' | 'external';
  supplier: string;
  supplierName: string;
  leadTime: number;
  costDifference: number;
  riskScore: 'low' | 'medium' | 'high';
  description: string;
}

interface AlertContext {
  alert: Alert;
  impactedPOs: any[];
}

interface AlertStore {
  // Monitoring configuration
  monitoringConfig: MonitoringConfig;
  
  // Safety Progression state
  selectedAlert: Alert | null;
  selectedAlertContext: AlertContext | null;
  selectedRecommendation: Recommendation | null;
  resolvedAlerts: string[];
  
  // Actions
  setMonitoringConfig: (config: Partial<MonitoringConfig>) => void;
  setSelectedAlert: (alert: Alert | null) => void;
  setSelectedAlertContext: (context: AlertContext | null) => void;
  setSelectedRecommendation: (rec: Recommendation | null) => void;
  resolveAlert: (alertId: string) => void;
  clearSafetyProgression: () => void;
}

export const useAlertStore = create<AlertStore>()(
  persist(
    (set) => ({
      // Initial state
      monitoringConfig: {
        riskCategory: 'ALL',
        impactThreshold: 500000,
        frequency: 'realtime',
        isActive: true,
      },
      selectedAlert: null,
      selectedAlertContext: null,
      selectedRecommendation: null,
      resolvedAlerts: [],
      
      // Actions
      setMonitoringConfig: (config) =>
        set((state) => ({
          monitoringConfig: { ...state.monitoringConfig, ...config },
        })),
      
      setSelectedAlert: (alert) => set({ selectedAlert: alert }),
      
      setSelectedAlertContext: (context) => set({ selectedAlertContext: context }),
      
      setSelectedRecommendation: (rec) => set({ selectedRecommendation: rec }),
      
      resolveAlert: (alertId) =>
        set((state) => ({
          resolvedAlerts: [...state.resolvedAlerts, alertId],
          selectedAlert: null,
          selectedAlertContext: null,
          selectedRecommendation: null,
        })),
      
      clearSafetyProgression: () =>
        set({
          selectedAlert: null,
          selectedAlertContext: null,
          selectedRecommendation: null,
        }),
    }),
    {
      name: 'alert-store',
      partialize: (state) => ({
        monitoringConfig: state.monitoringConfig,
        resolvedAlerts: state.resolvedAlerts,
      }),
    }
  )
);
