import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Grid,
  Skeleton,
  Chip,
  Stack,
  alpha,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { fetchLlmUsage, fetchTimeline, fetchFunnel, fetchAtsScores, fetchAnalyticsDashboard } from '../api';
import type { LlmUsage, FunnelStage, TimelinePoint } from '../types';

const kpiVariants = {
  hidden: { opacity: 0, y: 14 },
  show: (i: number) => ({ opacity: 1, y: 0, transition: { duration: 0.3, delay: i * 0.08, ease: [0.4, 0, 0.2, 1] } }),
};

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <Box sx={{ bgcolor: 'white', border: '1px solid', borderColor: 'divider', borderRadius: 2, px: 2, py: 1.5, boxShadow: 3 }}>
      <Typography variant="caption" color="text.secondary" display="block">{label}</Typography>
      {payload.map((p) => (
        <Typography key={p.name} variant="body2" fontWeight={600} sx={{ color: p.color }}>
          {p.name}: {p.name?.includes('Cost') ? `$${p.value.toFixed(4)}` : p.value}
        </Typography>
      ))}
    </Box>
  );
};

export default function Analytics() {
  const { data: llmData } = useQuery({ queryKey: ['llm-usage'], queryFn: fetchLlmUsage });
  const { data: timeline } = useQuery({ queryKey: ['timeline'], queryFn: fetchTimeline });
  const { data: funnel } = useQuery({ queryKey: ['funnel'], queryFn: fetchFunnel });
  const { data: atsScores } = useQuery({ queryKey: ['ats-scores'], queryFn: fetchAtsScores });
  const { data: analytics } = useQuery({ queryKey: ['analytics-dashboard'], queryFn: fetchAnalyticsDashboard });

  const totalCost = llmData?.reduce((s: number, item: LlmUsage) => s + (item.total_cost_usd ?? 0), 0) ?? 0;
  const totalCalls = llmData?.reduce((s: number, item: LlmUsage) => s + (item.total_requests ?? 0), 0) ?? 0;

  // Correct ATS avg: use analytics endpoint (backed by actual DB avg)
  const avgAts = Math.round((analytics?.avg_ats_score ?? 0) * 100);

  const llmByProvider = llmData?.reduce(
    (acc: Record<string, { provider: string; cost: number; calls: number }>, item: LlmUsage) => {
      if (!acc[item.provider]) acc[item.provider] = { provider: item.provider, cost: 0, calls: 0 };
      acc[item.provider].cost += item.total_cost_usd ?? 0;
      acc[item.provider].calls += item.total_requests ?? 1;
      return acc;
    },
    {}
  ) ?? {};

  const providerData = Object.values(llmByProvider);

  const conversionData = funnel?.slice(0, -1).map((stage: FunnelStage, idx: number) => ({
    stage: stage.stage,
    from: stage.count,
    to: funnel[idx + 1]?.count ?? 0,
    rate:
      funnel[idx + 1] && stage.count > 0
        ? Math.round(((funnel[idx + 1].count / stage.count) * 100) * 10) / 10
        : 0,
  })) ?? [];

  const kpis = [
    { label: 'LLM Calls', value: totalCalls.toLocaleString(), sub: 'Cover letters & analysis', color: '#0A66C2' },
    { label: 'Total LLM Cost', value: `$${totalCost.toFixed(4)}`, sub: 'Cumulative expense', color: '#7C3AED' },
    { label: 'Avg ATS Score', value: avgAts > 0 ? `${avgAts}%` : 'N/A', sub: 'Resume compatibility', color: '#D97706' },
  ];

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>Analytics</Typography>
        <Typography variant="body2" color="text.secondary">Detailed insights into your job search campaign</Typography>
      </Box>

      {/* KPI row */}
      <Grid container spacing={2.5} mb={3}>
        {kpis.map((k, i) => (
          <Grid item xs={12} sm={4} key={k.label}>
            <motion.div custom={i} variants={kpiVariants} initial="hidden" animate="show">
              <Card>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={500} display="block" mb={0.75}>
                    {k.label}
                  </Typography>
                  <Typography variant="h4" fontWeight={800} sx={{ color: k.color, mb: 0.5 }}>
                    {k.value}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">{k.sub}</Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Charts row */}
      <Grid container spacing={2.5} mb={2.5}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 310 }}>
            <CardHeader title="LLM Provider Usage" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 248, pt: 0 }}>
              {providerData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={providerData} margin={{ left: -20, right: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                    <XAxis dataKey="provider" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                    <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 12 }} />
                    <Bar yAxisId="left" dataKey="calls" fill="#0A66C2" name="API Calls" radius={[5, 5, 0, 0]} maxBarSize={48} />
                    <Bar yAxisId="right" dataKey="cost" fill="#D97706" name="Cost ($)" radius={[5, 5, 0, 0]} maxBarSize={48} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={210} sx={{ borderRadius: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: 310 }}>
            <CardHeader title="Application Activity (30d)" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 248, pt: 0 }}>
              {timeline && timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={(timeline as TimelinePoint[]).slice(-30)} margin={{ left: -20, right: 10 }}>
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
                    <Line type="monotone" dataKey="applications_applied" stroke="#059669" strokeWidth={2.5} dot={false} name="Applied" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={210} sx={{ borderRadius: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ATS distribution */}
      {atsScores && atsScores.length > 0 && (
        <Card sx={{ mb: 2.5 }}>
          <CardHeader title="ATS Score Distribution" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
          <CardContent sx={{ height: 220, pt: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={atsScores} margin={{ left: -20, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                <XAxis dataKey="range_label" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#7C3AED" radius={[5, 5, 0, 0]} name="Applications" maxBarSize={56} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Conversion table */}
      <Card sx={{ mb: 2.5 }}>
        <CardHeader title="Funnel Conversion Rates" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Stage</TableCell>
                <TableCell align="right">From</TableCell>
                <TableCell align="right">To</TableCell>
                <TableCell align="right">Conversion</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {conversionData.length > 0 ? (
                conversionData.map((row) => (
                  <TableRow key={row.stage}>
                    <TableCell sx={{ fontWeight: 500 }}>{row.stage}</TableCell>
                    <TableCell align="right">{row.from}</TableCell>
                    <TableCell align="right">{row.to}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${row.rate.toFixed(1)}%`}
                        size="small"
                        sx={{
                          bgcolor:
                            row.rate > 50
                              ? alpha('#059669', 0.1)
                              : row.rate > 20
                              ? alpha('#D97706', 0.1)
                              : alpha('#DC2626', 0.1),
                          color: row.rate > 50 ? '#059669' : row.rate > 20 ? '#D97706' : '#DC2626',
                          fontWeight: 700,
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                    No conversion data available
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* LLM usage detail */}
      <Card>
        <CardHeader title="LLM Usage Details" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Provider</TableCell>
                <TableCell>Model</TableCell>
                <TableCell align="right">Requests</TableCell>
                <TableCell align="right">Tokens</TableCell>
                <TableCell align="right">Cost</TableCell>
                <TableCell align="right">Avg Latency</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {llmData && llmData.length > 0 ? (
                llmData.slice(0, 20).map((item: LlmUsage, idx: number) => (
                  <TableRow key={idx}>
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#0A66C2', flexShrink: 0 }} />
                        <Typography variant="body2" fontWeight={500}>{item.provider}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ fontFamily: 'monospace', fontSize: 12 }}>{item.model ?? '—'}</Typography>
                    </TableCell>
                    <TableCell align="right">{item.total_requests ?? '—'}</TableCell>
                    <TableCell align="right">{item.total_tokens?.toLocaleString() ?? '—'}</TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600} color={item.total_cost_usd > 0.01 ? 'warning.main' : 'text.secondary'}>
                        ${(item.total_cost_usd ?? 0).toFixed(4)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="caption" color="text.secondary">
                        {item.avg_latency_ms ? `${Math.round(item.avg_latency_ms)}ms` : '—'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                    No LLM usage data yet
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
}
