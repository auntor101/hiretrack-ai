import { createTheme, alpha } from '@mui/material/styles';

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
      main: '#057642',
      light: '#0a8a4b',
      dark: '#03572e',
      contrastText: '#fff',
    },
    error: { main: '#CC1016' },
    warning: { main: '#E8820C' },
    info: { main: '#0288d1' },
    success: { main: '#057642' },
    background: {
      default: '#F3F2EF',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1D2226',
      secondary: '#56687A',
    },
    divider: '#E0DDD8',
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", system-ui, -apple-system, sans-serif',
    h1: { fontWeight: 800, letterSpacing: '-0.02em' },
    h2: { fontWeight: 700, letterSpacing: '-0.01em' },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 20, boxShadow: 'none', '&:hover': { boxShadow: 'none' } },
        containedPrimary: {
          background: 'linear-gradient(135deg, #0A66C2 0%, #004182 100%)',
          '&:hover': { background: 'linear-gradient(135deg, #004182 0%, #003166 100%)' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 0 0 1px #E0DDD8',
          borderRadius: 10,
          '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.10)', transform: 'translateY(-1px)', transition: 'all 0.2s ease' },
        },
      },
    },
    MuiChip: { styleOverrides: { root: { fontWeight: 500 } } },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: '#FFFFFF', color: '#1D2226', boxShadow: '0 0 0 1px #E0DDD8' },
      },
    },
    MuiDrawer: {
      styleOverrides: { paper: { borderRight: '1px solid #E0DDD8', backgroundColor: '#FFFFFF' } },
    },
    MuiLinearProgress: { styleOverrides: { root: { borderRadius: 4 } } },
  },
});

export const statusColors: Record<string, string> = {
  queued: '#56687A',
  pending_review: '#E8820C',
  applied: '#0A66C2',
  interview: '#7C3AED',
  offer: '#057642',
  rejected: '#CC1016',
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
  queued: alpha('#56687A', 0.12),
  pending_review: alpha('#E8820C', 0.12),
  applied: alpha('#0A66C2', 0.12),
  interview: alpha('#7C3AED', 0.12),
  offer: alpha('#057642', 0.12),
  rejected: alpha('#CC1016', 0.12),
};

export default theme;
