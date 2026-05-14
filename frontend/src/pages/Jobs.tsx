import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Pagination,
  Select,
  MenuItem,
  TextField,
  Typography,
  Stack,
  InputAdornment,
  alpha,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import WorkOutlineIcon from '@mui/icons-material/WorkOutline';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AddIcon from '@mui/icons-material/Add';
import { fetchJobs, createApplication } from '../api';

const PAGE_SIZE = 12;

const expFilters = [
  { value: 'all', label: 'Any Level' },
  { value: 'entry', label: 'Entry' },
  { value: 'mid', label: 'Mid' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
];

const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] } },
};
const grid = {
  hidden: {},
  show: { transition: { staggerChildren: 0.055 } },
};

export default function Jobs() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [remote, setRemote] = useState<'all' | 'remote' | 'onsite'>('all');
  const [expLevel, setExpLevel] = useState('all');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce search so we don't fire on every keystroke
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 350);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [search]);

  const params = {
    page,
    page_size: PAGE_SIZE,
    ...(debouncedSearch ? { search: debouncedSearch } : {}),
    ...(remote === 'remote' ? { remote: true } : remote === 'onsite' ? { remote: false } : {}),
    ...(expLevel !== 'all' ? { experience_level: expLevel } : {}),
  };

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['jobs', params],
    queryFn: () => fetchJobs(params),
  });

  const applyMutation = useMutation({
    mutationFn: (jobId: string) => createApplication({ job_id: jobId, apply_mode: 'review' }),
    onSuccess: () => {
      toast.success('Application queued for review');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
    onError: () => toast.error('Failed to create application'),
  });

  const totalPages = Math.ceil((data?.total ?? 0) / PAGE_SIZE);

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>Job Board</Typography>
        <Typography variant="body2" color="text.secondary">
          {data ? `${data.total.toLocaleString()} opportunities` : 'Loading…'}
        </Typography>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3, p: 2.5 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search by title, company, or location…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
                </InputAdornment>
              ),
            }}
          />
          <Select
            size="small"
            value={remote}
            onChange={(e) => { setRemote(e.target.value as typeof remote); setPage(1); }}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="all">All Locations</MenuItem>
            <MenuItem value="remote">Remote Only</MenuItem>
            <MenuItem value="onsite">On-site</MenuItem>
          </Select>
          <Select
            size="small"
            value={expLevel}
            onChange={(e) => { setExpLevel(e.target.value); setPage(1); }}
            sx={{ minWidth: 140 }}
          >
            {expFilters.map((f) => (
              <MenuItem key={f.value} value={f.value}>{f.label}</MenuItem>
            ))}
          </Select>
        </Stack>
      </Card>

      {(isLoading || isFetching) && (
        <LinearProgress sx={{ mb: 2, borderRadius: 2 }} />
      )}

      {/* Job grid */}
      <motion.div key={JSON.stringify(params)} variants={grid} initial="hidden" animate="show">
        <Grid container spacing={2.5} mb={3}>
          {data?.items.length === 0 && !isLoading && (
            <Grid item xs={12}>
              <Card sx={{ textAlign: 'center', py: 8 }}>
                <WorkOutlineIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1.5 }} />
                <Typography color="text.secondary">No jobs match your filters.</Typography>
              </Card>
            </Grid>
          )}
          {(data?.items ?? []).map((job) => (
            <Grid item xs={12} sm={6} lg={4} key={job.id}>
              <motion.div variants={cardVariants} style={{ height: '100%' }}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flex: 1, p: 2.5 }}>
                    <Typography variant="subtitle2" fontWeight={700} color="primary.main" mb={0.25}>
                      {job.title}
                    </Typography>
                    <Typography variant="body2" fontWeight={600} color="text.primary" mb={0.5}>
                      {job.company}
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={0.5} mb={1}>
                      <LocationOnOutlinedIcon sx={{ fontSize: 13, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary" noWrap>
                        {job.location}
                      </Typography>
                    </Stack>
                    {job.salary_range && (
                      <Stack direction="row" alignItems="center" spacing={0.25} mb={1}>
                        <AttachMoneyIcon sx={{ fontSize: 14, color: 'success.main' }} />
                        <Typography variant="caption" color="success.main" fontWeight={700}>
                          {job.salary_range}
                        </Typography>
                      </Stack>
                    )}
                    <Stack direction="row" spacing={0.75} flexWrap="wrap" gap={0.5}>
                      <Chip
                        label={job.remote ? 'Remote' : 'On-site'}
                        size="small"
                        color={job.remote ? 'success' : 'default'}
                        sx={{ bgcolor: job.remote ? alpha('#059669', 0.1) : undefined, color: job.remote ? 'success.main' : undefined }}
                      />
                      <Chip label={job.experience_level} size="small" />
                      {job.job_type && <Chip label={job.job_type} size="small" variant="outlined" />}
                    </Stack>
                  </CardContent>
                  <Box
                    sx={{
                      px: 2.5, py: 1.75,
                      borderTop: '1px solid',
                      borderColor: 'divider',
                      display: 'flex',
                      justifyContent: 'flex-end',
                      bgcolor: alpha('#0A66C2', 0.015),
                    }}
                  >
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<AddIcon sx={{ fontSize: '16px !important' }} />}
                      onClick={() => applyMutation.mutate(job.id)}
                      disabled={applyMutation.isPending}
                      sx={{ borderRadius: 20, px: 2.5, fontSize: 12 }}
                    >
                      Quick Apply
                    </Button>
                  </Box>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center">
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, v) => { setPage(v); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
            color="primary"
            shape="rounded"
          />
        </Box>
      )}
    </Box>
  );
}
