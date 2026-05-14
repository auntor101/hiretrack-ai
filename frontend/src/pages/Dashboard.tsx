import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Skeleton,
  Typography,
  Chip,
  Stack,
  alpha,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkOutlineIcon from '@mui/icons-material/WorkOutline';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { fetchDashboardStats, fetchFunnel, fetchTimeline, fetchAnalyticsDashboard } from '../api';
import { statusColors, statusLabels } from '../theme';

function useCountUp(end: number, duration = 1100) {
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

const kpiConfig = [
  {
    key: 'jobs',
    label: 'Total Jobs Found',
    icon: <WorkOutlineIcon />,
    color: '#0A66C2',
    bg: alpha('#0A66C2', 0.08),
  },
  {
    key: 'applications',
    label: 'Applications',
    icon: <AssignmentTurnedInIcon />,
    color: '#7C3AED',
    bg: alpha('#7C3AED', 0.08),
  },
  {
    key: 'ats',
    label: 'Avg ATS Score',
    icon: <TrendingUpIcon />,
    color: '#D97706',
    bg: alpha('#D97706', 0.08),
    suffix: '%',
  },
  {
    key: 'interviews',
    label: 'Interviews',
    icon: <EmojiEventsIcon />,
    color: '#059669',
    bg: alpha('#059669', 0.08),
  },
];

function KpiCard({
  label,
  value,
  suffix = '',
  icon,
  color,
  bg,
  delay,
}: {
  label: string;
  value: number;
  suffix?: string;
  icon: React.ReactNode;
  color: string;
  bg: string;
  delay: number;
}) {
  const count = useCountUp(value);
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.4, 0, 0.2, 1] }}
      style={{ height: '100%' }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ p: 2.5 }}>
          <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={500} display="block" mb={0.75}>
                {label}
              </Typography>
              <Typography variant="h3" fontWeight={800} sx={{ color, lineHeight: 1 }}>
                {count}{suffix}
              </Typography>
            </Box>
            <Box
              sx={{
                width: 44, height: 44, borderRadius: 2.5, bgcolor: bg,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color, flexShrink: 0,
              }}
            >
              {icon}
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <Box sx={{ bgcolor: 'white', border: '1px solid', borderColor: 'divider', borderRadius: 2, px: 2, py: 1.5, boxShadow: 3 }}>
      <Typography variant="caption" color="text.secondary" display="block">{label}</Typography>
      {payload.map((p) => (
        <Typography key={p.name} variant="body2" fontWeight={600} sx={{ color: p.color }}>
          {p.name}: {p.value}
        </Typography>
      ))}
    </Box>
  );
};

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchDashboardStats });
  const { data: analytics } = useQuery({ queryKey: ['analytics-dashboard'], queryFn: fetchAnalyticsDashboard });
  const { data: funnel } = useQuery({ queryKey: ['funnel'], queryFn: fetchFunnel });
  const { data: timeline } = useQuery({ queryKey: ['timeline'], queryFn: fetchTimeline });

  const byStatusChart = stats
    ? Object.entries(stats.by_status ?? {}).map(([key, val]) => ({
        status: statusLabels[key] ?? key,
        count: val,
        color: statusColors[key] ?? '#94A3B8',
      }))
    : [];

  const kpiValues = {
    jobs: analytics?.total_jobs_found ?? 0,
    applications: analytics?.total_applications ?? 0,
    ats: Math.round((analytics?.avg_ats_score ?? 0) * 100),
    interviews: analytics?.applications_interview ?? 0,
  };

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">Your job search performance at a glance</Typography>
      </Box>

      {/* KPIs */}
      <Grid container spacing={2.5} mb={3}>
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Grid item xs={12} sm={6} lg={3} key={i}>
                <Skeleton variant="rounded" height={96} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          : kpiConfig.map((k, i) => (
              <Grid item xs={12} sm={6} lg={3} key={k.key}>
                <KpiCard
                  label={k.label}
                  value={kpiValues[k.key as keyof typeof kpiValues]}
                  suffix={k.suffix}
                  icon={k.icon}
                  color={k.color}
                  bg={k.bg}
                  delay={i * 0.08}
                />
              </Grid>
            ))}
      </Grid>

      {/* Charts row */}
      <Grid container spacing={2.5} mb={2.5}>
        <Grid item xs={12} md={7}>
          <Card sx={{ height: 320 }}>
            <CardHeader
              title="Application Funnel"
              titleTypographyProps={{ fontWeight: 700, variant: 'h6' }}
            />
            <CardContent sx={{ height: 250, pt: 0 }}>
              {funnel && funnel.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={funnel} margin={{ left: -20, right: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                    <XAxis dataKey="stage" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#0A66C2" radius={[6, 6, 0, 0]} name="Applications" maxBarSize={56} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={220} sx={{ borderRadius: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ height: 320 }}>
            <CardHeader
              title="Status Breakdown"
              titleTypographyProps={{ fontWeight: 700, variant: 'h6' }}
            />
            <CardContent sx={{ height: 250, pt: 0 }}>
              {byStatusChart.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={byStatusChart}
                      dataKey="count"
                      nameKey="status"
                      cx="50%"
                      cy="45%"
                      outerRadius={82}
                      innerRadius={44}
                      paddingAngle={2}
                    >
                      {byStatusChart.map((entry) => (
                        <Cell key={entry.status} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => [v, 'Count']} />
                    <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" justifyContent="center" pt={2}>
                  <Skeleton variant="circular" width={160} height={160} />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Timeline */}
      <Card>
        <CardHeader
          title="Activity — Last 30 Days"
          titleTypographyProps={{ fontWeight: 700, variant: 'h6' }}
        />
        <CardContent sx={{ height: 260, pt: 0 }}>
          {timeline && timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeline.slice(-30)} margin={{ left: -20, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: '#64748B' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(d: string) => new Date(d).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="jobs_found" stroke="#0A66C2" strokeWidth={2.5} dot={false} name="Jobs Found" />
                <Line type="monotone" dataKey="applications_applied" stroke="#059669" strokeWidth={2.5} dot={false} name="Applications Sent" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Skeleton variant="rectangular" height={220} sx={{ borderRadius: 2 }} />
          )}
        </CardContent>
      </Card>

      {/* Top missing skills */}
      {stats?.top_missing_skills && stats.top_missing_skills.length > 0 && (
        <Card sx={{ mt: 2.5 }}>
          <CardHeader
            title="Top Missing Skills"
            subheader="Most common skill gaps across your applications"
            titleTypographyProps={{ fontWeight: 700, variant: 'h6' }}
            subheaderTypographyProps={{ variant: 'caption' }}
          />
          <CardContent>
            <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
              {stats.top_missing_skills.slice(0, 12).map((item) => {
                const skill = typeof item === 'string' ? item : (item as { skill: string }).skill;
                return (
                  <Chip
                    key={skill}
                    label={skill}
                    size="small"
                    variant="outlined"
                    sx={{ borderColor: alpha('#DC2626', 0.3), color: '#DC2626', bgcolor: alpha('#DC2626', 0.05) }}
                  />
                );
              })}
            </Stack>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
