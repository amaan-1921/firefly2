// src/hooks/useAlerts.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Alert } from '@/types/alert';

export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await apiClient.get<Alert[]>('/alerts');
      return res.data;
    },
    refetchInterval: 60_000, // 60 seconds
    staleTime: 30_000,
    refetchOnWindowFocus: true
  });
}
