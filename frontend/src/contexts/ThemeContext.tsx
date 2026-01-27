'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ThemeMode } from '@/styles/theme';

interface ThemeContextType {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [themeMode, setThemeModeState] = useState<ThemeMode>('light');

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('themeMode') as ThemeMode;
    if (savedTheme && ['light', 'dark', 'company'].includes(savedTheme)) {
      setThemeModeState(savedTheme);
    }
  }, []);

  // Save theme to localStorage when it changes
  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode);
    localStorage.setItem('themeMode', mode);
  };

  return (
    <ThemeContext.Provider value={{ themeMode, setThemeMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
