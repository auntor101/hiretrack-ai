import axios from 'axios';
import type {
  JobsResponse,
  ApplicationsResponse,
  Application,
  DashboardStats,
  AnalyticsDashboard,
  FunnelStage,
  AtsScore,
  TimelinePoint,
  LlmUsage,
  Settings,
  LlmProvider,
} from './types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export const fetchJobs = (params: {
  page?: number;
  page_size?: number;
  remote?: boolean | null;
  search?: string;
  job_type?: string;
  experience_level?: string;
}): Promise<JobsResponse> =>
  api.get('/jobs', { params }).then((r) => r.data);

export const fetchApplications = (params: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<ApplicationsResponse> =>
  api.get('/applications', { params }).then((r) => r.data);

export const createApplication = (data: {
  job_id: string;
  apply_mode?: string;
}): Promise<Application> => api.post('/applications/', data).then((r) => r.data);

export const updateApplicationStatus = (
  id: string,
  data: { status: string; notes?: string }
): Promise<Application> =>
  api.put(`/applications/${id}/status`, data).then((r) => r.data);

export const scoreResume = (id: string): Promise<{ ats_score: number; details: string }> =>
  api.post(`/applications/${id}/score-resume`).then((r) => r.data);

export const getSkillGap = (
  id: string
): Promise<{ matched_skills: string[]; missing_skills: string[] }> =>
  api.post(`/applications/${id}/skill-gap`).then((r) => r.data);

export const generateCoverLetter = (id: string): Promise<{ cover_letter: string }> =>
  api.post(`/applications/${id}/cover-letter`).then((r) => r.data);

export const fetchDashboardStats = (): Promise<DashboardStats> =>
  api.get('/dashboard/stats').then((r) => r.data);

export const fetchAnalyticsDashboard = (): Promise<AnalyticsDashboard> =>
  api.get('/analytics/dashboard').then((r) => r.data);

export const fetchFunnel = (): Promise<FunnelStage[]> =>
  api.get('/analytics/funnel').then((r) => r.data);

export const fetchAtsScores = (): Promise<AtsScore[]> =>
  api.get('/analytics/ats-scores').then((r) => r.data);

export const fetchTimeline = (): Promise<TimelinePoint[]> =>
  api.get('/analytics/timeline').then((r) => r.data);

export const fetchLlmUsage = (): Promise<LlmUsage[]> =>
  api.get('/analytics/llm-usage').then((r) => r.data);

export const fetchSettings = (): Promise<Settings> =>
  api.get('/settings').then((r) => r.data);

export const updateSettings = (data: Partial<Settings>): Promise<Settings> =>
  api.put('/settings', data).then((r) => r.data);

export const fetchLlmProviders = (): Promise<LlmProvider[]> =>
  api.get('/settings/llm-providers').then((r) => r.data);
