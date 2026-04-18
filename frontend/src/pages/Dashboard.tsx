import { useQuery } from '@tanstack/react-query';
import { Box, Card, CardContent, CardHeader, Grid, Skeleton, Typography } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { fetchDashboardStats, fetchFunnel, fetchTimeline, fetchAnalyticsDashboard } from '../api';
import { statusColors, statusLabels } from '../theme';

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchDashboardStats });
  const { data: analytics } = useQuery({ queryKey: ['analytics-dashboard'], queryFn: fetchAnalyticsDashboard });
  const { data: funnel } = useQuery({ queryKey: ['funnel'], queryFn: fetchFunnel });
  const { data: timeline } = useQuery({ queryKey: ['timeline'], queryFn: fetchTimeline });

  const byStatusChart = stats ? Object.entries(stats.by_status ?? {}).map(([key, val]) => ({ status: statusLabels[key] ?? key, count: val, color: statusColors[key] ?? '#999' })) : [];

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={0.5}>Dashboard</Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>Your job search performance at a glance</Typography>

      <Grid container spacing={2.5} mb={3}>
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => <Grid item xs={12} sm={6} lg={3} key={i}><Skeleton variant="rectangular" height={100} /></Grid>)
          : [
              { label: 'Total Jobs', value: analytics?.total_jobs_found ?? 0, color: '#0A66C2' },
              { label: 'Applications', value: analytics?.total_applications ?? 0, color: '#7C3AED' },
              { label: 'Avg ATS Score', value: `${Math.round((analytics?.avg_ats_score ?? 0) * 100)}%`, color: '#E8820C' },
              { label: 'Interviews', value: analytics?.applications_interview ?? 0, color: '#057642' },
            ].map((kpi) => (
              <Grid item xs={12} sm={6} lg={3} key={kpi.label}>
                <Card>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" mb={0.5}>{kpi.label}</Typography>
                    <Typography variant="h4" fontWeight={800} color={kpi.color}>{kpi.value}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))
        }
      </Grid>

      <Grid container spacing={2.5} mb={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 300 }}>
            <CardHeader title="Application Funnel" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 240 }}>
              {funnel && funnel.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={funnel} margin={{ left: -30 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="stage" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0A66C2" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={200} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: 300 }}>
            <CardHeader title="Status Breakdown" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 240 }}>
              {byStatusChart.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={byStatusChart} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} paddingAngle={2}>
                      {byStatusChart.map((entry) => <Cell key={entry.status} fill={entry.color} />)}
                    </Pie>
                    <Tooltip formatter={(v: any) => [v, 'Count']} />
                    <Legend iconType="circle" iconSize={10} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="circular" width={160} height={160} sx={{ mx: 'auto' }} />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardHeader title="Activity Timeline (Last 30 days)" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
        <CardContent sx={{ height: 250 }}>
          {timeline && timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeline.slice(-30)} margin={{ left: -30 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => new Date(d).toLocaleDateString('en', { month: 'short', day: 'numeric' })} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip labelFormatter={(d: any) => new Date(d).toLocaleDateString('en', { month: 'long', day: 'numeric' })} />
                <Legend />
                <Line type="monotone" dataKey="jobs_found" stroke="#0A66C2" strokeWidth={2} dot={false} name="Jobs Found" />
                <Line type="monotone" dataKey="applications_applied" stroke="#057642" strokeWidth={2} dot={false} name="Applications Sent" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Skeleton variant="rectangular" height={220} />
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
