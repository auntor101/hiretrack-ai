import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Box, Button, Card, CardContent, Chip, Grid, LinearProgress, Pagination, Select, MenuItem, TextField, Typography, Stack, InputAdornment, Alert } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { fetchJobs, createApplication } from '../api';

const PAGE_SIZE = 12;

export default function Jobs() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [remote, setRemote] = useState('all');
  const [snack, setSnack] = useState<string | null>(null);

  const params = { page, page_size: PAGE_SIZE, ...(remote === 'remote' ? { remote: true } : remote === 'onsite' ? { remote: false } : {}) };
  const { data, isLoading } = useQuery({ queryKey: ['jobs', params], queryFn: () => fetchJobs(params) });

  const applyMutation = useMutation({
    mutationFn: (jobId: string) => createApplication({ job_id: jobId, apply_mode: 'review' }),
    onSuccess: () => { setSnack('Application queued! ✓'); queryClient.invalidateQueries({ queryKey: ['applications'] }); setTimeout(() => setSnack(null), 2000); },
    onError: () => { setSnack('Failed to apply'); },
  });

  const totalPages = Math.ceil((data?.total ?? 0) / PAGE_SIZE);

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>Job Board</Typography>
        <Typography variant="body1" color="text.secondary">{data ? `${data.total} opportunities found` : 'Loading…'}</Typography>
      </Box>

      <Card sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search by title, company, or skill…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: 'text.secondary' }} /></InputAdornment> }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Select
              fullWidth
              size="small"
              value={remote}
              onChange={(e) => { setRemote(e.target.value); setPage(1); }}
            >
              <MenuItem value="all">All Locations</MenuItem>
              <MenuItem value="remote">Remote Only</MenuItem>
              <MenuItem value="onsite">On-site</MenuItem>
            </Select>
          </Grid>
        </Grid>
      </Card>

      {isLoading && <LinearProgress sx={{ mb: 2, borderRadius: 2 }} />}
      {snack && <Alert severity={snack.includes('✓') ? 'success' : 'error'} sx={{ mb: 2 }}>{snack}</Alert>}

      <Grid container spacing={2.5} mb={3}>
        {(data?.items ?? []).map((job) => (
          <Grid item xs={12} sm={6} lg={4} key={job.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1 }}>
                <Typography variant="subtitle1" fontWeight={700} color="primary.main">{job.title}</Typography>
                <Typography variant="body2" fontWeight={600} mb={1}>{job.company}</Typography>
                <Typography variant="caption" color="text.secondary">{job.location}</Typography>
                {job.salary_range && (
                  <Typography variant="caption" color="success.main" fontWeight={600} display="block" my={1}>{job.salary_range}</Typography>
                )}
                <Stack direction="row" spacing={0.75} flexWrap="wrap" gap={0.5}>
                  <Chip label={job.remote ? '🌐 Remote' : 'On-site'} size="small" color={job.remote ? 'success' : 'default'} sx={{ fontWeight: 600, fontSize: 11 }} />
                  <Chip label={job.experience_level} size="small" sx={{ fontSize: 11 }} />
                </Stack>
              </CardContent>
              <Box sx={{ px: 2, py: 1.5, borderTop: '1px solid #E0DDD8', display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => applyMutation.mutateAsync(job.id)}
                  sx={{ borderRadius: 20, px: 2 }}
                >
                  Quick Apply
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center">
          <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} color="primary" shape="rounded" />
        </Box>
      )}
    </Box>
  );
}
