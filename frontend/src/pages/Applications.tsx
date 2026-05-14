import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  LinearProgress,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  alpha,
  Tooltip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SchoolIcon from '@mui/icons-material/School';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import { fetchApplications, fetchDashboardStats, generateInterviewPrep } from '../api';
import { statusColors, statusLabels, statusBgs } from '../theme';
import type { Application, InterviewPrepResult } from '../types';

const PAGE_SIZE = 20;

const STATUS_ORDER = ['queued', 'pending_review', 'applied', 'interview', 'offer', 'rejected'];

const rowVariants = {
  hidden: { opacity: 0, x: -8 },
  show: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: { duration: 0.22, delay: i * 0.03, ease: [0.4, 0, 0.2, 1] },
  }),
};

function InterviewPrepDialog({
  app,
  open,
  onClose,
}: {
  app: Application;
  open: boolean;
  onClose: () => void;
}) {
  const [result, setResult] = useState<InterviewPrepResult | null>(null);
  const mutation = useMutation({
    mutationFn: () => generateInterviewPrep(app.id),
    onSuccess: (data) => setResult(data),
    onError: () => toast.error('Failed to generate questions. Check your LLM configuration.'),
  });

  const handleGenerate = () => {
    setResult(null);
    mutation.mutate();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" fontWeight={700}>Interview Prep</Typography>
            <Typography variant="caption" color="text.secondary">
              {app.job?.title ?? ''} · {app.job?.company ?? ''}
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {!result && !mutation.isPending && (
          <Box textAlign="center" py={4}>
            <SchoolIcon sx={{ fontSize: 52, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h6" fontWeight={700} mb={1}>
              Ready to ace your interview?
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3} maxWidth={400} mx="auto">
              Generate 6 tailored questions — 3 technical and 3 behavioral — with key talking points and tips for this specific role.
            </Typography>
            <Button variant="contained" color="secondary" onClick={handleGenerate} size="large" sx={{ borderRadius: 25, px: 4 }}>
              Generate Questions
            </Button>
          </Box>
        )}

        {mutation.isPending && (
          <Box py={4}>
            <LinearProgress color="secondary" sx={{ borderRadius: 2, mb: 2 }} />
            <Typography textAlign="center" color="text.secondary" variant="body2">
              Generating interview questions…
            </Typography>
          </Box>
        )}

        {result && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" mb={2}>
              {result.questions.length} questions for {result.job_title} at {result.company}
            </Typography>
            <AnimatePresence>
              {result.questions.map((q, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                >
                  <Accordion
                    disableGutters
                    elevation={0}
                    sx={{
                      mb: 1.5,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: '10px !important',
                      '&:before': { display: 'none' },
                    }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Stack direction="row" spacing={1.5} alignItems="flex-start">
                        <Box
                          sx={{
                            width: 24, height: 24, borderRadius: '50%',
                            bgcolor: i < 3 ? alpha('#0A66C2', 0.1) : alpha('#7C3AED', 0.1),
                            color: i < 3 ? 'primary.main' : 'secondary.main',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 12, fontWeight: 700, flexShrink: 0, mt: 0.25,
                          }}
                        >
                          {i + 1}
                        </Box>
                        <Typography variant="body2" fontWeight={600} lineHeight={1.5}>
                          {q.question}
                        </Typography>
                      </Stack>
                    </AccordionSummary>
                    <AccordionDetails sx={{ pt: 0, pb: 2, px: 2.5 }}>
                      {q.key_points.length > 0 && (
                        <Box mb={1.5}>
                          <Typography variant="caption" fontWeight={700} color="text.secondary" display="block" mb={0.75}>
                            KEY POINTS TO ADDRESS
                          </Typography>
                          {q.key_points.map((pt, j) => (
                            <Stack key={j} direction="row" spacing={1} alignItems="flex-start" mb={0.5}>
                              <Box sx={{ width: 5, height: 5, borderRadius: '50%', bgcolor: 'primary.main', mt: 0.65, flexShrink: 0 }} />
                              <Typography variant="body2" color="text.secondary">{pt}</Typography>
                            </Stack>
                          ))}
                        </Box>
                      )}
                      {q.tip && (
                        <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ bgcolor: alpha('#D97706', 0.07), borderRadius: 2, p: 1.25 }}>
                          <TipsAndUpdatesIcon sx={{ fontSize: 16, color: 'warning.main', mt: 0.1, flexShrink: 0 }} />
                          <Typography variant="caption" color="text.secondary">{q.tip}</Typography>
                        </Stack>
                      )}
                    </AccordionDetails>
                  </Accordion>
                </motion.div>
              ))}
            </AnimatePresence>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        {result && (
          <Button onClick={handleGenerate} variant="outlined" color="secondary" sx={{ mr: 'auto' }}>
            Regenerate
          </Button>
        )}
        <Button onClick={onClose} variant="contained">Close</Button>
      </DialogActions>
    </Dialog>
  );
}

export default function Applications() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [prepApp, setPrepApp] = useState<Application | null>(null);

  const queryParams = {
    page,
    page_size: PAGE_SIZE,
    ...(statusFilter !== 'all' ? { status: statusFilter } : {}),
  };

  const { data, isLoading } = useQuery({
    queryKey: ['applications', queryParams],
    queryFn: () => fetchApplications(queryParams),
  });

  // Use aggregate stats for accurate status counts (not just current page)
  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
  });

  const apps = data?.items ?? [];
  const totalPages = Math.ceil((data?.total ?? 0) / PAGE_SIZE);
  const byStatus = stats?.by_status ?? {};

  return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>My Applications</Typography>
          <Typography variant="body2" color="text.secondary">{data?.total ?? 0} total applications</Typography>
        </Box>
        <Button
          variant="outlined"
          href="/api/v1/applications/export"
          target="_blank"
          sx={{ borderRadius: 10 }}
        >
          Export CSV
        </Button>
      </Box>

      {isLoading && <LinearProgress sx={{ mb: 2, borderRadius: 2 }} />}

      {/* Status summary chips */}
      <Grid container spacing={1.5} mb={3}>
        {STATUS_ORDER.map((status) => {
          const count = byStatus[status] ?? 0;
          const isActive = statusFilter === status;
          return (
            <Grid item xs={6} sm={4} md={2} key={status}>
              <Card
                onClick={() => setStatusFilter(isActive ? 'all' : status)}
                sx={{
                  cursor: 'pointer',
                  border: isActive ? `2px solid ${statusColors[status]}` : '2px solid transparent',
                  transition: 'all 0.18s ease',
                  '&:hover': { borderColor: statusColors[status] },
                }}
              >
                <CardContent sx={{ p: '12px 14px !important' }}>
                  <Chip
                    label={statusLabels[status]}
                    size="small"
                    sx={{
                      bgcolor: statusBgs[status],
                      color: statusColors[status],
                      fontWeight: 600,
                      fontSize: 10,
                      mb: 0.75,
                      height: 22,
                    }}
                  />
                  <Typography variant="h5" fontWeight={800} color={statusColors[status]}>
                    {count}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Card>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Role</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">ATS Score</TableCell>
              <TableCell>Applied</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <AnimatePresence mode="wait">
              {apps.map((app, i) => (
                <motion.tr
                  key={app.id}
                  custom={i}
                  variants={rowVariants}
                  initial="hidden"
                  animate="show"
                  exit={{ opacity: 0 }}
                  style={{ display: 'table-row' }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 200 }}>
                      {app.job?.title ?? '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {app.job?.company ?? '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={statusLabels[app.status] ?? app.status}
                      size="small"
                      sx={{
                        bgcolor: statusBgs[app.status],
                        color: statusColors[app.status],
                        fontWeight: 600,
                        fontSize: 11,
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {app.ats_score != null ? (
                      <Chip
                        label={`${Math.round(app.ats_score * 100)}%`}
                        size="small"
                        sx={{
                          bgcolor:
                            app.ats_score >= 0.75
                              ? alpha('#059669', 0.1)
                              : app.ats_score >= 0.5
                              ? alpha('#D97706', 0.1)
                              : alpha('#DC2626', 0.1),
                          color:
                            app.ats_score >= 0.75
                              ? '#059669'
                              : app.ats_score >= 0.5
                              ? '#D97706'
                              : '#DC2626',
                          fontWeight: 700,
                        }}
                      />
                    ) : (
                      <Typography variant="caption" color="text.secondary">—</Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '—'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {app.status === 'interview' && (
                      <Tooltip title="AI Interview Prep">
                        <Button
                          variant="contained"
                          color="secondary"
                          size="small"
                          onClick={() => setPrepApp(app)}
                          sx={{ borderRadius: 20, fontSize: 11, px: 1.5, py: 0.5, minWidth: 0 }}
                        >
                          Prep
                        </Button>
                      </Tooltip>
                    )}
                  </TableCell>
                </motion.tr>
              ))}
            </AnimatePresence>
            {apps.length === 0 && !isLoading && (
              <TableRow>
                <TableCell colSpan={6} sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
                  No applications found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} color="primary" shape="rounded" />
        </Box>
      )}

      {prepApp && (
        <InterviewPrepDialog
          app={prepApp}
          open={!!prepApp}
          onClose={() => setPrepApp(null)}
        />
      )}
    </Box>
  );
}
