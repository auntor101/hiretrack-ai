import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import WorkRoundedIcon from '@mui/icons-material/WorkRounded';
import AssignmentRoundedIcon from '@mui/icons-material/AssignmentRounded';
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded';
import BarChartRoundedIcon from '@mui/icons-material/BarChartRounded';
import SettingsRoundedIcon from '@mui/icons-material/SettingsRounded';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { SIDEBAR_WIDTH } from './theme';

const navItems = [
  { label: 'Home', path: '/', icon: <HomeRoundedIcon fontSize="small" /> },
  { label: 'Job Board', path: '/jobs', icon: <WorkRoundedIcon fontSize="small" /> },
  { label: 'Applications', path: '/applications', icon: <AssignmentRoundedIcon fontSize="small" /> },
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardRoundedIcon fontSize="small" /> },
  { label: 'Analytics', path: '/analytics', icon: <BarChartRoundedIcon fontSize="small" /> },
  { label: 'Settings', path: '/settings', icon: <SettingsRoundedIcon fontSize="small" /> },
];

const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.22, ease: [0.4, 0, 0.2, 1] } },
  exit: { opacity: 0, y: -6, transition: { duration: 0.15 } },
};

function SidebarContent({ onNavigate }: { onNavigate: () => void }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(180deg, #0C1526 0%, #0F172A 50%, #1A1F35 100%)',
      }}
    >
      {/* Brand */}
      <Box sx={{ px: 2.5, py: 3, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 38, height: 38, borderRadius: 2.5,
            background: 'linear-gradient(135deg, #0A66C2 0%, #378FE9 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(10,102,194,0.45)',
            flexShrink: 0,
          }}
        >
          <AutoAwesomeIcon sx={{ color: 'white', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography
            variant="subtitle1"
            sx={{ color: 'white', fontWeight: 800, lineHeight: 1.15, letterSpacing: '-0.01em', fontSize: 15 }}
          >
            HireTrack AI
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.38)', fontSize: 11, letterSpacing: '0.02em' }}>
            Job Search Assistant
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.07)', mx: 2 }} />

      <List sx={{ px: 1.5, py: 1.5, flex: 1 }}>
        {navItems.map((item) => {
          const active =
            item.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.path);

          return (
            <ListItemButton
              key={item.path}
              onClick={() => { navigate(item.path); onNavigate(); }}
              selected={active}
              sx={{
                borderRadius: 2.5,
                mb: 0.5,
                px: 1.75,
                py: 1.1,
                color: active ? '#ffffff' : 'rgba(255,255,255,0.5)',
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.15s ease',
                '&::before': active ? {
                  content: '""',
                  position: 'absolute',
                  left: 0,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: 3,
                  height: '60%',
                  borderRadius: '0 3px 3px 0',
                  backgroundColor: '#378FE9',
                } : {},
                '&.Mui-selected': {
                  bgcolor: 'rgba(55,143,233,0.14)',
                  color: '#ffffff',
                  '& .MuiListItemIcon-root': { color: '#378FE9' },
                  '&:hover': { bgcolor: 'rgba(55,143,233,0.18)' },
                },
                '&:hover': {
                  bgcolor: 'rgba(255,255,255,0.06)',
                  color: 'rgba(255,255,255,0.85)',
                },
                '& .MuiListItemIcon-root': {
                  color: active ? '#378FE9' : 'rgba(255,255,255,0.35)',
                  minWidth: 36,
                  transition: 'color 0.15s ease',
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: 13.5,
                  fontWeight: active ? 600 : 400,
                  letterSpacing: active ? '-0.01em' : 0,
                }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Box sx={{ px: 2.5, py: 2, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.2)', fontSize: 11, letterSpacing: '0.02em' }}>
          v1.0 · LiteLLM + FastAPI
        </Typography>
      </Box>
    </Box>
  );
}

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Mobile AppBar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          display: { md: 'none' },
          zIndex: (t) => t.zIndex.drawer + 1,
          bgcolor: '#0C1526',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
        }}
      >
        <Toolbar sx={{ minHeight: '52px !important' }}>
          <IconButton
            onClick={() => setMobileOpen(true)}
            edge="start"
            sx={{ mr: 1, color: 'rgba(255,255,255,0.8)' }}
          >
            <MenuIcon />
          </IconButton>
          <AutoAwesomeIcon sx={{ color: '#378FE9', mr: 1, fontSize: 20 }} />
          <Typography variant="h6" fontWeight={800} sx={{ color: 'white', fontSize: 16 }}>
            HireTrack AI
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: SIDEBAR_WIDTH, border: 'none' },
        }}
      >
        <SidebarContent onNavigate={() => setMobileOpen(false)} />
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: SIDEBAR_WIDTH, boxSizing: 'border-box', border: 'none' },
        }}
        open
      >
        <SidebarContent onNavigate={() => {}} />
      </Drawer>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flex: 1,
          minWidth: 0,
          mt: { xs: '52px', md: 0 },
          p: { xs: 2.5, md: 3.5 },
          maxWidth: '100%',
          overflowX: 'hidden',
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </Box>
    </Box>
  );
}
