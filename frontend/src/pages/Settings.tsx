import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Box, Card, CardContent, Tab, Tabs, Typography, TextField, Switch, FormControlLabel, FormGroup, Stack, Button, Chip, Grid, MenuItem, Skeleton, Alert } from '@mui/material';
import { fetchSettings, updateSettings, fetchLlmProviders } from '../api';
import type { Settings as SettingsResponse } from '../types';

// Defined at module scope to avoid remounting (and losing focus/state) on every
// parent re-render caused by tab changes or form input.
interface TabPanelProps { children: React.ReactNode; value: number; index: number; }
function TabPanel({ children, value, index }: TabPanelProps) {
  return value === index ? <Box sx={{ pt: 2 }}>{children}</Box> : null;
}

export default function Settings() {
  const [tabValue, setTabValue] = useState(0);
  const { data: settings, isLoading } = useQuery({ queryKey: ['settings'], queryFn: fetchSettings });
  const { data: providers, isLoading: providersLoading } = useQuery({ queryKey: ['llm-providers'], queryFn: fetchLlmProviders });
  const [formData, setFormData] = useState<Partial<SettingsResponse>>({});
  const updateMutation = useMutation({ mutationFn: updateSettings });

  React.useEffect(() => {
    if (settings) setFormData(settings);
  }, [settings]);

  const handleChange = (field: string, value: unknown) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSave = async () => {
    await updateMutation.mutateAsync(formData);
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={0.5}>Settings</Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>Configure your job search automation</Typography>

      <Card>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Pipeline Configuration" />
          <Tab label="AI Providers" />
          <Tab label="Preferences" />
        </Tabs>

        <CardContent>
          <TabPanel value={tabValue} index={0}>
            {isLoading ? (
              <Stack spacing={2}>
                {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} variant="text" height={40} />)}
              </Stack>
            ) : (
              <Stack spacing={2.5}>
                <Typography variant="h6" fontWeight={700} mb={1}>Auto-Apply Settings</Typography>
                <FormGroup>
                  <FormControlLabel
                    control={<Switch checked={formData.auto_apply_enabled ?? false} onChange={(e) => handleChange('auto_apply_enabled', e.target.checked)} />}
                    label="Enable automatic job application"
                  />
                </FormGroup>

                <TextField label="Max Applications Per Day" type="number" value={formData.max_applications_per_day ?? 10} onChange={(e) => handleChange('max_applications_per_day', parseInt(e.target.value))} fullWidth />

                <TextField label="Min ATS Score Required (%)" type="number" inputProps={{ min: 0, max: 100, step: 5 }} value={formData.min_ats_score ?? 60} onChange={(e) => handleChange('min_ats_score', parseInt(e.target.value))} fullWidth />

                <TextField select label="Cover Letter Template" value={formData.cover_letter_template ?? 'standard'} onChange={(e) => handleChange('cover_letter_template', e.target.value)} fullWidth>
                  {['standard', 'creative', 'technical'].map((t) => <MenuItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</MenuItem>)}
                </TextField>

                <TextField select label="Resume Template" value={formData.resume_template ?? 'modern'} onChange={(e) => handleChange('resume_template', e.target.value)} fullWidth>
                  {['modern', 'classic', 'executive', 'minimal', 'creative'].map((t) => <MenuItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</MenuItem>)}
                </TextField>

                <Box>
                  <FormControlLabel control={<Switch checked={formData.personalize_cover_letter ?? true} onChange={(e) => handleChange('personalize_cover_letter', e.target.checked)} />} label="Personalize cover letters automatically" />
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>Uses AI to customize each cover letter to the job description</Typography>
                </Box>

                <Box>
                  <FormControlLabel control={<Switch checked={formData.skip_application_form ?? false} onChange={(e) => handleChange('skip_application_form', e.target.checked)} />} label="Skip application forms if possible" />
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>Applies via resume/CV only for Apply with Resume jobs</Typography>
                </Box>

                <Button variant="contained" onClick={handleSave} disabled={updateMutation.isPending} sx={{ mt: 1 }}>
                  {updateMutation.isPending ? 'Saving...' : 'Save Pipeline Settings'}
                </Button>
              </Stack>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {providersLoading ? (
              <Stack spacing={2}>
                {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} variant="rectangular" height={100} />)}
              </Stack>
            ) : (
              <Stack spacing={2.5}>
                <Typography variant="h6" fontWeight={700} mb={1}>AI Model Providers</Typography>
                <Alert severity="info">APIs are called in order of priority. Ensure valid API keys in your environment.</Alert>

                <Grid container spacing={2}>
                  {providers && providers.length > 0
                    ? providers.map((p: any) => (
                        <Grid item xs={12} sm={6} md={4} key={p.name}>
                          <Card variant="outlined">
                            <CardContent>
                              <Stack spacing={1} alignItems="center" textAlign="center">
                                <Chip label={p.name} size="small" color={p.configured ? 'success' : 'default'} variant={p.configured ? 'filled' : 'outlined'} />
                                <Typography variant="body2">{p.name_display ?? p.name}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {p.configured ? '✓ Configured' : '⚠ Not configured'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ fontSize: 11, fontFamily: 'monospace' }}>
                                  {p.default_model ?? 'N/A'}
                                </Typography>
                              </Stack>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))
                    : (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary" textAlign="center"> No providers configured</Typography>
                        </Grid>
                      )}
                </Grid>

                <Box sx={{ mt: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="body2" fontWeight={600} mb={1}>Setup Instructions</Typography>
                  <Typography variant="caption" component="div" color="text.secondary">
                    1. Set environment variables for each provider (OPENAI_API_KEY, GROQ_API_KEY, etc.)
                  </Typography>
                  <Typography variant="caption" component="div" color="text.secondary">
                    2. Restart the backend service for changes to take effect
                  </Typography>
                  <Typography variant="caption" component="div" color="text.secondary">
                    3. Monitor costs and usage in the Analytics tab
                  </Typography>
                </Box>
              </Stack>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {isLoading ? (
              <Stack spacing={2}>
                {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} variant="text" height={40} />)}
              </Stack>
            ) : (
              <Stack spacing={2.5}>
                <Typography variant="h6" fontWeight={700} mb={1}>Job Preferences</Typography>

                <TextField label="Target Job Roles (comma-separated)" multiline rows={2} value={formData.target_roles ?? ''} onChange={(e) => handleChange('target_roles', e.target.value)} fullWidth placeholder="Software Engineer, Data Scientist, Product Manager" />

                <TextField label="Target Locations (comma-separated)" multiline rows={2} value={formData.target_locations ?? ''} onChange={(e) => handleChange('target_locations', e.target.value)} fullWidth placeholder="San Francisco, New York, Remote" />

                <TextField label="Min Annual Salary ($)" type="number" value={formData.min_salary ?? 100000} onChange={(e) => handleChange('min_salary', parseInt(e.target.value))} fullWidth />

                <TextField label="Max Commute Distance (miles)" type="number" value={formData.max_commute ?? 30} onChange={(e) => handleChange('max_commute', parseInt(e.target.value))} fullWidth />

                <Box>
                  <FormControlLabel control={<Switch checked={formData.remote_only ?? false} onChange={(e) => handleChange('remote_only', e.target.checked)} />} label="Remote-only jobs" />
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>Only apply to fully remote positions</Typography>
                </Box>

                <Box>
                  <FormControlLabel control={<Switch checked={formData.exclude_contract ?? true} onChange={(e) => handleChange('exclude_contract', e.target.checked)} />} label="Exclude contract/temp work" />
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>Only apply to permanent full-time roles</Typography>
                </Box>

                <TextField select label="Work Authorization" value={formData.preferred_sponsorship ?? 'not_required'} onChange={(e) => handleChange('preferred_sponsorship', e.target.value)} fullWidth>
                  <MenuItem value="not_required">No visa sponsorship needed</MenuItem>
                  <MenuItem value="ok_with_sponsorship">Open to sponsorship</MenuItem>
                  <MenuItem value="require_sponsorship">Require sponsorship</MenuItem>
                </TextField>

                <TextField label="Years of Experience (desired)" type="number" value={formData.years_experience ?? 5} onChange={(e) => handleChange('years_experience', parseInt(e.target.value))} fullWidth />

                <TextField label="Resume File Path" value={formData.resume_path ?? '/data/resume.pdf'} onChange={(e) => handleChange('resume_path', e.target.value)} fullWidth />

                <Button variant="contained" onClick={handleSave} disabled={updateMutation.isPending} sx={{ mt: 1 }}>
                  {updateMutation.isPending ? 'Saving...' : 'Save Preferences'}
                </Button>
              </Stack>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
