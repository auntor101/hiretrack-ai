import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Skeleton,
  Typography,
  Stack,
  alpha,
} from '@mui/material';
import WorkRoundedIcon from '@mui/icons-material/WorkRounded';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { fetchDashboardStats, fetchJobs } from '../api';

function useCountUp(end: number, duration = 1200) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (end === 0) { setValue(0); return; }
    let raf: number;
    const start = performance.now();
    const animate = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(Math.round(eased * end));
      if (t < 1) raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [end, duration]);
  return value;
}

const features = [
  {
    icon: <AutoAwesomeIcon sx={{ fontSize: 26 }} />,
    color: '#0A66C2',
    bg: alpha('#0A66C2', 0.08),
    title: 'AI-Powered Matching',
    desc: 'LLM-based scoring analyzes your resume against every job description and surfaces the best fits instantly.',
  },
  {
    icon: <TrendingUpIcon sx={{ fontSize: 26 }} />,
    color: '#7C3AED',
    bg: alpha('#7C3AED', 0.08),
    title: 'ATS Score Optimizer',
    desc: 'Know your compatibility score before you apply. Spot skill gaps and fix them with concrete suggestions.',
  },
  {
    icon: <CheckCircleOutlineIcon sx={{ fontSize: 26 }} />,
    color: '#059669',
    bg: alpha('#059669', 0.08),
    title: 'Auto Cover Letters',
    desc: 'Tailored cover letters generated in seconds for every application using your preferred LLM provider.',
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};
const cardItem = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.4, 0, 0.2, 1] } },
};

function StatItem({ label, rawValue, suffix = '' }: { label: string; rawValue: number; suffix?: string }) {
  const count = useCountUp(rawValue);
  return (
    <Box>
      <Typography variant="h4" color="white" fontWeight={800} lineHeight={1}>
        {count}{suffix}
      </Typography>
      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>
        {label}
      </Typography>
    </Box>
  );
}

export default function Home() {
  const navigate = useNavigate();
  const { data: stats } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchDashboardStats });
  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', { page: 1, page_size: 6 }],
    queryFn: () => fetchJobs({ page: 1, page_size: 6 }),
  });

  return (
    <Box>
      {/* Hero */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #0C1526 0%, #0F172A 45%, #1A1035 100%)',
          borderRadius: 4,
          p: { xs: 4, md: 5.5 },
          mb: 4,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Decorative orbs */}
        <Box sx={{ position: 'absolute', top: -100, right: -80, width: 340, height: 340, borderRadius: '50%', background: alpha('#0A66C2', 0.12), filter: 'blur(60px)', pointerEvents: 'none' }} />
        <Box sx={{ position: 'absolute', bottom: -80, left: '30%', width: 280, height: 280, borderRadius: '50%', background: alpha('#7C3AED', 0.1), filter: 'blur(60px)', pointerEvents: 'none' }} />

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <Stack direction="row" spacing={1.5} alignItems="center" mb={2.5}>
            <Box sx={{ width: 36, height: 36, borderRadius: 2, background: 'linear-gradient(135deg, #0A66C2, #378FE9)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(10,102,194,0.4)' }}>
              <AutoAwesomeIcon sx={{ color: 'white', fontSize: 18 }} />
            </Box>
            <Chip label="AI-Powered Job Search" size="small" sx={{ bgcolor: alpha('#fff', 0.1), color: 'white', fontWeight: 600, fontSize: 12 }} />
          </Stack>

          <Typography
            variant="h3"
            sx={{ color: 'white', fontWeight: 800, mb: 2, maxWidth: 580, lineHeight: 1.15 }}
          >
            Your Job Search{' '}
            <Box component="span" sx={{ background: 'linear-gradient(90deg, #378FE9, #A78BFA)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Command Center
            </Box>
          </Typography>

          <Typography
            variant="body1"
            sx={{ color: 'rgba(255,255,255,0.68)', mb: 4, maxWidth: 480, lineHeight: 1.7, fontSize: '1.05rem' }}
          >
            Discover roles, score your ATS compatibility, generate tailored cover letters, and track every application — all from one place.
          </Typography>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/jobs')}
              startIcon={<WorkRoundedIcon />}
              endIcon={<ArrowForwardIcon />}
              sx={{
                bgcolor: 'white',
                color: 'primary.main',
                borderRadius: 25,
                px: 3.5,
                py: 1.4,
                fontWeight: 700,
                fontSize: '0.9rem',
                '&:hover': { bgcolor: '#F0F4FA', transform: 'translateY(-1px)', boxShadow: '0 8px 20px rgba(0,0,0,0.2)' },
                background: 'white',
              }}
            >
              Browse Jobs
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/dashboard')}
              sx={{
                borderColor: 'rgba(255,255,255,0.25)',
                color: 'rgba(255,255,255,0.85)',
                borderRadius: 25,
                px: 3.5,
                py: 1.4,
                fontWeight: 600,
                fontSize: '0.9rem',
                '&:hover': { borderColor: 'rgba(255,255,255,0.6)', bgcolor: alpha('#fff', 0.07) },
              }}
            >
              View Dashboard
            </Button>
          </Stack>
        </motion.div>

        {stats && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 0.4 }}>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={{ xs: 2, sm: 4 }}
              mt={4}
              pt={3.5}
              sx={{ borderTop: '1px solid rgba(255,255,255,0.1)', flexWrap: 'wrap' }}
            >
              <StatItem label="Total Applications" rawValue={stats.total_applications} />
              <StatItem label="Interviews" rawValue={stats.by_status?.interview ?? 0} />
              <StatItem label="Offers" rawValue={stats.by_status?.offer ?? 0} />
              <StatItem label="Avg ATS Score" rawValue={Math.round((stats.avg_ats_score ?? 0) * 100)} suffix="%" />
            </Stack>
          </motion.div>
        )}
      </Box>

      {/* Feature cards */}
      <motion.div variants={container} initial="hidden" animate="show">
        <Grid container spacing={2.5} mb={4}>
          {features.map((f) => (
            <Grid item xs={12} md={4} key={f.title}>
              <motion.div variants={cardItem} style={{ height: '100%' }}>
                <Card sx={{ height: '100%' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      sx={{
                        width: 48, height: 48, borderRadius: 3, bgcolor: f.bg,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: f.color, mb: 2,
                      }}
                    >
                      {f.icon}
                    </Box>
                    <Typography variant="subtitle1" fontWeight={700} mb={0.75}>{f.title}</Typography>
                    <Typography variant="body2" color="text.secondary" lineHeight={1.65}>{f.desc}</Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {/* Latest opportunities */}
      <Box mb={2.5} display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="h5" fontWeight={700}>Latest Opportunities</Typography>
        <Button
          variant="text"
          onClick={() => navigate('/jobs')}
          endIcon={<ArrowForwardIcon sx={{ fontSize: 16 }} />}
          size="small"
          sx={{ color: 'primary.main', fontWeight: 600 }}
        >
          View all
        </Button>
      </Box>

      <motion.div variants={container} initial="hidden" animate="show">
        <Grid container spacing={2}>
          {jobsLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Grid item xs={12} sm={6} lg={4} key={i}>
                  <Card>
                    <CardContent>
                      <Skeleton variant="text" width="60%" height={22} />
                      <Skeleton variant="text" width="40%" height={18} />
                      <Skeleton variant="text" width="50%" height={16} />
                    </CardContent>
                  </Card>
                </Grid>
              ))
            : jobs?.items.map((job) => (
                <Grid item xs={12} sm={6} lg={4} key={job.id}>
                  <motion.div variants={cardItem}>
                    <Card
                      sx={{ height: '100%', cursor: 'pointer' }}
                      onClick={() => navigate('/jobs')}
                    >
                      <CardContent sx={{ p: 2.5 }}>
                        <Typography variant="subtitle2" fontWeight={700} color="primary.main" noWrap mb={0.25}>
                          {job.title}
                        </Typography>
                        <Typography variant="body2" fontWeight={600} color="text.primary" noWrap mb={0.75}>
                          {job.company}
                        </Typography>
                        <Stack direction="row" alignItems="center" spacing={0.5} mb={1.25}>
                          <LocationOnOutlinedIcon sx={{ fontSize: 13, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary" noWrap>
                            {job.location}
                          </Typography>
                        </Stack>
                        {job.salary_range && (
                          <Typography variant="caption" color="success.main" fontWeight={700} display="block" mb={1}>
                            {job.salary_range}
                          </Typography>
                        )}
                        <Stack direction="row" spacing={0.75} flexWrap="wrap" gap={0.5}>
                          <Chip
                            label={job.remote ? 'Remote' : 'On-site'}
                            size="small"
                            color={job.remote ? 'success' : 'default'}
                          />
                          <Chip label={job.experience_level} size="small" />
                        </Stack>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
        </Grid>
      </motion.div>
    </Box>
  );
}
