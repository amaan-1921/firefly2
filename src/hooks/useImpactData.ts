// src/hooks/useImpactData.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { PO } from '@/types/po';

export function useImpactData(alertId: string | null) {
  return useQuery<PO[]>({
    queryKey: ['impact', alertId],
    queryFn: async () => {
      if (!alertId) return [];
      const res = await apiClient.get<PO[]>(`/impact?alertId=${alertId}`);
      return res.data;
    },
    enabled: Boolean(alertId),
    staleTime: 30_000
  });
}
