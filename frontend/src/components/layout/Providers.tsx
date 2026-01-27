'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { SessionProvider } from 'next-auth/react';
import { getTheme } from '@/styles/theme';
import { ThemeProvider as CustomThemeProvider, useTheme as useCustomTheme } from '@/contexts/ThemeContext';

const queryClient = new QueryClient();

export default function Providers({ children }: { children: React.ReactNode }) {
  // Inner component to use theme context
  const ThemeWrapper = ({ children }: { children: React.ReactNode }) => {
    const { themeMode } = useCustomTheme();
    const currentTheme = getTheme(themeMode);

    return (
      <ThemeProvider theme={currentTheme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    );
  };

  return (
    <CustomThemeProvider>
      <SessionProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeWrapper>
            {children}
            <ReactQueryDevtools initialIsOpen={false} />
          </ThemeWrapper>
        </QueryClientProvider>
      </SessionProvider>
    </CustomThemeProvider>
  );
}
