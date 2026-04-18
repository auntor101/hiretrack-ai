import { useQuery } from '@tanstack/react-query';
import { Box, Card, CardContent, CardHeader, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography, Grid, Skeleton } from '@mui/material';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchLlmUsage, fetchTimeline, fetchFunnel, fetchAtsScores } from '../api';
import type { LlmUsage, FunnelStage, TimelinePoint, AtsScore } from '../types';

export default function Analytics() {
  const { data: llmData } = useQuery({ queryKey: ['llm-usage'], queryFn: fetchLlmUsage });
  const { data: timeline } = useQuery({ queryKey: ['timeline'], queryFn: fetchTimeline });
  const { data: funnel } = useQuery({ queryKey: ['funnel'], queryFn: fetchFunnel });
  const { data: atsScores } = useQuery({ queryKey: ['ats-scores'], queryFn: fetchAtsScores });

  const llmByProvider = llmData?.reduce((acc: Record<string, { provider: string; cost: number; calls: number }>, item: LlmUsage) => {
    if (!acc[item.provider]) acc[item.provider] = { provider: item.provider, cost: 0, calls: 0 };
    acc[item.provider].cost += item.total_cost_usd ?? 0;
    acc[item.provider].calls += item.total_requests ?? 1;
    return acc;
  }, {}) ?? {};

  const providerData = Object.values(llmByProvider);
  const costByDay = timeline?.map((t: TimelinePoint) => ({ date: t.date, cost: (t.applications_applied ?? 0) * 0.01 })) ?? [];
  const conversionData = funnel?.slice(0, -1).map((stage: FunnelStage, idx: number) => ({
    stage: stage.stage,
    from: stage.count,
    to: funnel[idx + 1]?.count ?? 0,
    rate: funnel[idx + 1] && stage.count > 0 ? Math.round(((funnel[idx + 1].count / stage.count) * 100) * 10) / 10 : 0,
  })) ?? [];

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={0.5}>Analytics</Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>Detailed insights into your job search campaign</Typography>

      <Grid container spacing={2.5} mb={3}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" mb={0.5}>Total LLM Calls</Typography>
              <Typography variant="h4" fontWeight={800}>{llmData?.length ?? 0}</Typography>
              <Typography variant="caption" color="text.secondary">Cover letters & resume analysis</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" mb={0.5}>Total LLM Cost</Typography>
              <Typography variant="h4" fontWeight={800}>${(llmData?.reduce((s: number, item: LlmUsage) => s + (item.total_cost_usd ?? 0), 0) ?? 0).toFixed(2)}</Typography>
              <Typography variant="caption" color="text.secondary">Cumulative expense</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" mb={0.5}>Avg ATS Score</Typography>
              <Typography variant="h4" fontWeight={800}>{atsScores && atsScores.length > 0 ? `${Math.round((atsScores.reduce((s: number, a: AtsScore) => s + (a.count ?? 0), 0) / atsScores.length) * 100)}%` : 'N/A'}</Typography>
              <Typography variant="caption" color="text.secondary">Resume compatibility</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.5} mb={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 300 }}>
            <CardHeader title="LLM Provider Usage" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 240 }}>
              {providerData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={providerData} margin={{ left: -30 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="provider" tick={{ fontSize: 10 }} />
                    <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="calls" fill="#0A66C2" name="API Calls" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="right" dataKey="cost" fill="#E8820C" name="Cost ($)" radius={[4, 4, 0, 0]} />
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
            <CardHeader title="Daily Cost Trends" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
            <CardContent sx={{ height: 240 }}>
              {costByDay.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={costByDay.slice(-30)} margin={{ left: -30 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d: any) => new Date(d).toLocaleDateString('en', { month: 'short', day: 'numeric' })} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip labelFormatter={(d: any) => new Date(d).toLocaleDateString('en', { month: 'long', day: 'numeric' })} formatter={(v: any) => `$${(v as number).toFixed(2)}`} />
                    <Line type="monotone" dataKey="cost" stroke="#E8820C" strokeWidth={2} dot={false} name="Daily Cost" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={200} />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardHeader title="Funnel Conversion Rates" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 700 }}>Stage</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>From Count</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>To Count</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>Conversion Rate</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {conversionData.length > 0 ? (
                conversionData.map((row: any) => (
                  <TableRow key={row.stage}>
                    <TableCell sx={{ fontWeight: 500 }}>{row.stage}</TableCell>
                    <TableCell align="right">{row.from}</TableCell>
                    <TableCell align="right">{row.to}</TableCell>
                    <TableCell align="right" sx={{ color: row.rate > 50 ? '#057642' : row.rate > 25 ? '#E8820C' : '#A2271D' }}>
                      {row.rate.toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} sx={{ textAlign: 'center', py: 3 }}>No conversion data available</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Card sx={{ mt: 2.5 }}>
        <CardHeader title="LLM Usage Details" titleTypographyProps={{ fontWeight: 700, variant: 'h6' }} />
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 700 }}>Provider</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Model</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>Tokens</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>Cost</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Purpose</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {llmData && llmData.length > 0 ? (
                llmData.slice(0, 20).map((item: LlmUsage, idx: number) => (
                  <TableRow key={idx}>
                    <TableCell sx={{ fontWeight: 500 }}>{item.provider}</TableCell>
                    <TableCell>{item.model ?? '-'}</TableCell>
                    <TableCell align="right">{item.total_tokens ?? '-'}</TableCell>
                    <TableCell align="right">${(item.total_cost_usd ?? 0).toFixed(4)}</TableCell>
                    <TableCell>{'-'}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: 'center', py: 3 }}>No LLM usage data yet</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {llmData && llmData.length > 20 && (
          <Typography variant="caption" color="text.secondary" sx={{ p: 1.5, display: 'block', textAlign: 'center' }}>
            Showing 20 of {llmData.length} records
          </Typography>
        )}
      </Card>
    </Box>
  );
}
