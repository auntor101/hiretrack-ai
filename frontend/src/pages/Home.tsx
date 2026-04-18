import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Box, Button, Card, CardContent, Chip, Grid, Skeleton, Typography, Stack, alpha } from '@mui/material';
import WorkRoundedIcon from '@mui/icons-material/WorkRounded';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import { fetchDashboardStats, fetchJobs } from '../api';

const features = [
  { icon: <AutoAwesomeIcon sx={{ fontSize: 28, color: '#0A66C2' }} />, title: 'AI-Powered Matching', desc: 'GPT-4 analyzes your resume and scores job fit automatically.' },
  { icon: <TrendingUpIcon sx={{ fontSize: 28, color: '#7C3AED' }} />, title: 'ATS Score Optimizer', desc: 'Know your ATS score before you apply and fix skill gaps instantly.' },
  { icon: <CheckCircleOutlineIcon sx={{ fontSize: 28, color: '#057642' }} />, title: 'Auto Cover Letters', desc: 'Tailored cover letters generated in seconds for every application.' },
];

export default function Home() {
  const navigate = useNavigate();
  const { data: stats } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchDashboardStats });
  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', { page: 1, page_size: 6 }],
    queryFn: () => fetchJobs({ page: 1, page_size: 6 }),
  });

  return (
    <Box>
      <Box sx={{ background: 'linear-gradient(135deg, #0A66C2 0%, #004182 60%, #1a1a2e 100%)', borderRadius: 4, p: { xs: 4, md: 6 }, mb: 4, position: 'relative', overflow: 'hidden' }}>
        <Box sx={{ position: 'absolute', top: -80, right: -80, width: 320, height: 320, borderRadius: '50%', background: alpha('#378FE9', 0.15) }} />

        <Stack direction="row" spacing={1.5} alignItems="center" mb={2}>
          <AutoAwesomeIcon sx={{ color: '#FFD700', fontSize: 28 }} />
          <Chip label="AI-Powered" size="small" sx={{ bgcolor: alpha('#fff', 0.15), color: '#fff', fontWeight: 600 }} />
        </Stack>

        <Typography variant="h3" color="white" fontWeight={800} mb={1.5} sx={{ maxWidth: 600 }}>
          Your AI Job Search <Box component="span" sx={{ color: '#FFD700' }}>Command Center</Box>
        </Typography>

        <Typography variant="h6" color="rgba(255,255,255,0.8)" mb={3} fontWeight={400} sx={{ maxWidth: 500 }}>
          HireTrack AI automates your job hunt — from discovering roles to scoring ATS compatibility, generating cover letters, and tracking every application in real time.
        </Typography>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/jobs')}
            startIcon={<WorkRoundedIcon />}
            sx={{ bgcolor: 'white', color: 'primary.main', px: 3, py: 1.25, borderRadius: 25, fontWeight: 700, '&:hover': { bgcolor: 'grey.100' } }}
          >
            Browse 300+ Jobs
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate('/dashboard')}
            sx={{ borderColor: 'rgba(255,255,255,0.5)', color: 'white', px: 3, py: 1.25, borderRadius: 25, fontWeight: 600, '&:hover': { borderColor: 'white', bgcolor: alpha('#fff', 0.08) } }}
          >
            View Dashboard
          </Button>
        </Stack>

        {stats && (
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} mt={4} pt={3} sx={{ borderTop: '1px solid rgba(255,255,255,0.15)' }}>
            {[
              { label: 'Total Applications', value: stats.total_applications },
              { label: 'Interviews', value: stats.by_status?.interview ?? 0 },
              { label: 'Offers', value: stats.by_status?.offer ?? 0 },
              { label: 'Avg ATS Score', value: `${Math.round((stats.avg_ats_score ?? 0) * 100)}%` },
            ].map((s) => (
              <Box key={s.label}>
                <Typography variant="h4" color="white" fontWeight={800}>{s.value}</Typography>
                <Typography variant="caption" color="rgba(255,255,255,0.65)">{s.label}</Typography>
              </Box>
            ))}
          </Stack>
        )}
      </Box>

      <Grid container spacing={2.5} mb={4}>
        {features.map((f) => (
          <Grid item xs={12} md={4} key={f.title}>
            <Card sx={{ height: '100%', p: 0.5 }}>
              <CardContent>
                <Box mb={1.5}>{f.icon}</Box>
                <Typography variant="subtitle1" fontWeight={700} mb={0.5}>{f.title}</Typography>
                <Typography variant="body2" color="text.secondary">{f.desc}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box mb={2} display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="h5" fontWeight={700}>Latest Opportunities</Typography>
        <Button variant="text" onClick={() => navigate('/jobs')} size="small">View all 300+ →</Button>
      </Box>

      <Grid container spacing={2}>
        {jobsLoading
          ? Array.from({ length: 6 }).map((_, i) => (
              <Grid item xs={12} sm={6} lg={4} key={i}>
                <Card><CardContent><Skeleton variant="text" width="60%" height={24} /><Skeleton variant="text" width="40%" /></CardContent></Card>
              </Grid>
            ))
          : jobs?.items.map((job) => (
              <Grid item xs={12} sm={6} lg={4} key={job.id}>
                <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => navigate('/jobs')}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={700} color="primary.main" noWrap>{job.title}</Typography>
                    <Typography variant="body2" fontWeight={500} noWrap mb={0.5}>{job.company}</Typography>
                    <Stack direction="row" alignItems="center" spacing={0.5} mb={1}>
                      <LocationOnOutlinedIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary" noWrap>{job.location}</Typography>
                    </Stack>
                    {job.salary_range && (
                      <Typography variant="caption" color="success.main" fontWeight={600} display="block" mb={1}>{job.salary_range}</Typography>
                    )}
                    <Stack direction="row" spacing={0.75} flexWrap="wrap" gap={0.5}>
                      <Chip label={job.remote ? 'Remote' : 'On-site'} size="small" color={job.remote ? 'success' : 'default'} sx={{ fontSize: 11 }} />
                      <Chip label={job.experience_level} size="small" sx={{ fontSize: 11 }} />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
      </Grid>
    </Box>
  );
}
