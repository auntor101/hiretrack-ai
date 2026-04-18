import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Box, Button, Card, CardContent, Chip, Grid, Table, TableBody, TableCell, TableHead, TableRow, Typography, LinearProgress, Pagination } from '@mui/material';
import { fetchApplications } from '../api';
import { statusColors, statusLabels, statusBgs } from '../theme';

const PAGE_SIZE = 20;

export default function Applications() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useQuery({
    queryKey: ['applications', page],
    queryFn: () => fetchApplications({ page, page_size: PAGE_SIZE }),
  });

  const apps = data?.items ?? [];
  const totalPages = Math.ceil((data?.total ?? 0) / PAGE_SIZE);
  const byStatus: Record<string, number> = {};
  ['queued', 'pending_review', 'applied', 'interview', 'offer', 'rejected'].forEach((s) => {
    byStatus[s] = apps.filter((a) => a.status === s).length;
  });

  return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>My Applications</Typography>
          <Typography variant="body1" color="text.secondary">{data?.total ?? 0} total</Typography>
        </Box>
        <Button variant="outlined" href="/api/v1/applications/export" target="_blank">Export CSV</Button>
      </Box>

      {isLoading && <LinearProgress sx={{ mb: 2, borderRadius: 2 }} />}

      <Grid container spacing={2} mb={3}>
        {Object.entries(byStatus).map(([status, count]) => (
          <Grid item xs={6} sm={4} md={2} key={status}>
            <Card>
              <CardContent>
                <Chip
                  label={statusLabels[status]}
                  size="small"
                  sx={{ bgcolor: statusBgs[status], color: statusColors[status], fontWeight: 600, fontSize: 11, mb: 1 }}
                />
                <Typography variant="h6" fontWeight={800}>{count}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Role</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Company</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 700 }} align="right">ATS Score</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Applied</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {apps.map((app) => (
              <TableRow key={app.id} hover>
                <TableCell>{app.job?.title ?? '—'}</TableCell>
                <TableCell>{app.job?.company ?? '—'}</TableCell>
                <TableCell>
                  <Chip
                    label={statusLabels[app.status] ?? app.status}
                    size="small"
                    sx={{ bgcolor: statusBgs[app.status], color: statusColors[app.status], fontWeight: 600, fontSize: 11 }}
                  />
                </TableCell>
                <TableCell align="right">
                  {app.ats_score != null ? `${Math.round(app.ats_score * 100)}%` : '—'}
                </TableCell>
                <TableCell>{app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '—'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={2}>
          <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} color="primary" shape="rounded" />
        </Box>
      )}
    </Box>
  );
}
