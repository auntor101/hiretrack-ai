import { createTheme, alpha } from '@mui/material/styles';

export const SIDEBAR_WIDTH = 260;

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0A66C2',
      light: '#378FE9',
      dark: '#004182',
      contrastText: '#fff',
    },
    secondary: {
      main: '#7C3AED',
      light: '#A78BFA',
      dark: '#5B21B6',
      contrastText: '#fff',
    },
    error: { main: '#DC2626' },
    warning: { main: '#D97706' },
    info: { main: '#0EA5E9' },
    success: { main: '#059669' },
    background: {
      default: '#F0F4FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#0F172A',
      secondary: '#64748B',
    },
    divider: '#E2E8F0',
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", system-ui, -apple-system, sans-serif',
    h1: { fontWeight: 800, letterSpacing: '-0.025em' },
    h2: { fontWeight: 700, letterSpacing: '-0.02em' },
    h3: { fontWeight: 700, letterSpacing: '-0.015em' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    button: { fontWeight: 600, textTransform: 'none', letterSpacing: '0.01em' },
    body1: { lineHeight: 1.6 },
    body2: { lineHeight: 1.5 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          boxShadow: 'none',
          '&:hover': { boxShadow: 'none' },
          transition: 'all 0.18s cubic-bezier(0.4,0,0.2,1)',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #0A66C2 0%, #1570E0 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #004182 0%, #0A66C2 100%)',
            transform: 'translateY(-1px)',
            boxShadow: '0 6px 16px rgba(10,102,194,0.35)',
          },
        },
        containedSecondary: {
          background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5B21B6 0%, #7C3AED 100%)',
            transform: 'translateY(-1px)',
            boxShadow: '0 6px 16px rgba(124,58,237,0.35)',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': { borderWidth: '1.5px' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 0 0 1px rgba(15,23,42,0.05), 0 2px 8px rgba(15,23,42,0.04)',
          borderRadius: 14,
          transition: 'box-shadow 0.2s cubic-bezier(0.4,0,0.2,1), transform 0.2s cubic-bezier(0.4,0,0.2,1)',
          '&:hover': {
            boxShadow: '0 0 0 1px rgba(15,23,42,0.07), 0 10px 28px rgba(15,23,42,0.09)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 8,
          fontSize: '0.75rem',
          height: 26,
        },
        sizeSmall: { height: 24 },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { borderRadius: 6, height: 6 },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            transition: 'box-shadow 0.15s ease',
            '&:hover': {
              boxShadow: '0 0 0 3px rgba(10,102,194,0.08)',
            },
            '&.Mui-focused': {
              boxShadow: '0 0 0 3px rgba(10,102,194,0.15)',
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: { borderRadius: 10 },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          textTransform: 'none',
          fontSize: '0.875rem',
          letterSpacing: 0,
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: 'background 0.12s ease',
          '&:hover': {
            backgroundColor: alpha('#0A66C2', 0.028),
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 700,
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: '#64748B',
          backgroundColor: '#F8FAFC',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          boxShadow: '0 25px 60px rgba(15,23,42,0.18)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: { borderColor: '#E2E8F0' },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 10 },
      },
    },
  },
});

export const statusColors: Record<string, string> = {
  queued: '#64748B',
  pending_review: '#D97706',
  applied: '#0A66C2',
  interview: '#7C3AED',
  offer: '#059669',
  rejected: '#DC2626',
};

export const statusLabels: Record<string, string> = {
  queued: 'Queued',
  pending_review: 'Pending Review',
  applied: 'Applied',
  interview: 'Interview',
  offer: 'Offer',
  rejected: 'Rejected',
};

export const statusBgs: Record<string, string> = {
  queued: alpha('#64748B', 0.10),
  pending_review: alpha('#D97706', 0.10),
  applied: alpha('#0A66C2', 0.10),
  interview: alpha('#7C3AED', 0.10),
  offer: alpha('#059669', 0.10),
  rejected: alpha('#DC2626', 0.10),
};

export const statusIcons: Record<string, string> = {
  queued: '○',
  pending_review: '◑',
  applied: '→',
  interview: '◆',
  offer: '★',
  rejected: '✕',
};

export default theme;
