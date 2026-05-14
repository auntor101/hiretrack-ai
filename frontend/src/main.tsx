import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import App from './App';
import theme from './theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3500,
            style: {
              borderRadius: '10px',
              fontFamily: 'Inter, system-ui, sans-serif',
              fontSize: '14px',
              fontWeight: 500,
              boxShadow: '0 4px 20px rgba(15,23,42,0.12)',
            },
            success: { iconTheme: { primary: '#059669', secondary: '#fff' } },
            error: { iconTheme: { primary: '#DC2626', secondary: '#fff' } },
          }}
        />
        <App />
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
