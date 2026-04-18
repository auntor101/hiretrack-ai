import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
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

const DRAWER_WIDTH = 240;

const navItems = [
  { label: 'Home', path: '/', icon: <HomeRoundedIcon /> },
  { label: 'Job Board', path: '/jobs', icon: <WorkRoundedIcon /> },
  { label: 'Applications', path: '/applications', icon: <AssignmentRoundedIcon /> },
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardRoundedIcon /> },
  { label: 'Analytics', path: '/analytics', icon: <BarChartRoundedIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsRoundedIcon /> },
];

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ px: 2.5, py: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box sx={{ width: 36, height: 36, borderRadius: 2, background: 'linear-gradient(135deg, #0A66C2, #378FE9)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <AutoAwesomeIcon sx={{ color: 'white', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="subtitle1" fontWeight={700} color="primary.main" lineHeight={1.1}>
            HireTrack AI
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Job Manager
          </Typography>
        </Box>
      </Box>

      <Divider />

      <List sx={{ px: 1.5, py: 1, flex: 1 }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.path}
              onClick={() => { navigate(item.path); setMobileOpen(false); }}
              selected={active}
              sx={{ borderRadius: 2, mb: 0.5, '&.Mui-selected': { bgcolor: 'primary.main', color: 'white', '& .MuiListItemIcon-root': { color: 'white' }, '&:hover': { bgcolor: 'primary.dark' } } }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 14, fontWeight: active ? 600 : 400 }} />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="fixed" sx={{ display: { md: 'none' }, zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton onClick={() => setMobileOpen(true)} edge="start" sx={{ mr: 1 }}>
            <MenuIcon />
          </IconButton>
          <AutoAwesomeIcon sx={{ color: 'primary.main', mr: 1 }} />
          <Typography variant="h6" fontWeight={700} color="primary.main">
            HireTrack AI
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}
      >
        {drawer}
      </Drawer>

      <Drawer
        variant="permanent"
        sx={{ display: { xs: 'none', md: 'block' }, width: DRAWER_WIDTH, flexShrink: 0, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' } }}
        open
      >
        {drawer}
      </Drawer>

      <Box component="main" sx={{ flex: 1, minWidth: 0, mt: { xs: '56px', md: 0 }, p: { xs: 2, md: 3 }, maxWidth: '100%' }}>
        <Outlet />
      </Box>
    </Box>
  );
}
