import { createTheme, Theme } from '@mui/material/styles';

export type ThemeMode = 'light' | 'dark' | 'company';

// Light Theme
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#E57373',
      light: '#FFCDD2',
      dark: '#D32F2F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#D84315',
      light: '#FF7043',
      dark: '#BF360C',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#81C784',
      light: '#A5D6A7',
      dark: '#66BB6A',
    },
    warning: {
      main: '#FFB74D',
      light: '#FFCC80',
      dark: '#FFA726',
    },
    error: {
      main: '#E57373',
      light: '#EF9A9A',
      dark: '#F44336',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FAFAFA',
    },
    text: {
      primary: '#374151',
      secondary: '#6B7280',
      disabled: '#9CA3AF',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Dark Theme
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#FF5252',
      light: '#FF8A80',
      dark: '#D32F2F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FF7043',
      light: '#FFAB91',
      dark: '#E64A19',
      contrastText: '#000000',
    },
    success: {
      main: '#69F0AE',
      light: '#B9F6CA',
      dark: '#00E676',
    },
    warning: {
      main: '#FFD740',
      light: '#FFE57F',
      dark: '#FFC400',
    },
    error: {
      main: '#FF5252',
      light: '#FF8A80',
      dark: '#FF1744',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
      disabled: '#6B6B6B',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// ABB Company Theme
export const companyTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#FF000F',
      light: '#FF4D54',
      dark: '#CC000C',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#2C2C2C',
      light: '#4A4A4A',
      dark: '#000000',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#00A651',
      light: '#4CAF50',
      dark: '#007A3D',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    error: {
      main: '#FF000F',
      light: '#FF4D54',
      dark: '#CC000C',
    },
    background: {
      default: '#FFFFFF',
      paper: '#F5F5F5',
    },
    text: {
      primary: '#000000',
      secondary: '#4A4A4A',
      disabled: '#9E9E9E',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Get theme by mode
export const getTheme = (mode: ThemeMode): Theme => {
  switch (mode) {
    case 'dark':
      return darkTheme;
    case 'company':
      return companyTheme;
    case 'light':
    default:
      return lightTheme;
  }
};

// Export default as light theme for backwards compatibility
export const muiTheme = lightTheme;
