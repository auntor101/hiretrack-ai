export interface SkillsRequired {
  required: string[];
  preferred?: string[];
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  job_type: string;
  remote: boolean;
  experience_level: string;
  description?: string;
  skills_required: SkillsRequired;
  posted_date?: string;
  status: string;
}

export interface JobsResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface Application {
  id: string;
  job_id: string;
  status: string;
  apply_mode: string;
  ats_score?: number;
  cover_letter_path?: string;
  applied_at?: string;
  response_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  job?: Job;
}

export interface ApplicationsResponse {
  items: Application[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardStats {
  total_applications: number;
  by_status: Record<string, number>;
  avg_ats_score: number;
  top_missing_skills: string[];
}

export interface AnalyticsDashboard {
  total_jobs_found: number;
  total_applications: number;
  applications_interview: number;
  applications_offer: number;
  avg_ats_score: number;
}

export interface FunnelStage {
  stage: string;
  count: number;
}

export interface AtsScore {
  range_label: string;
  count: number;
}

export interface TimelinePoint {
  date: string;
  jobs_found: number;
  applications_created: number;
  applications_applied: number;
}

export interface LlmUsage {
  provider: string;
  model: string;
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
}

export interface Settings {
  llm_provider: string;
  llm_model: string;
  max_applications_per_day: number;
  auto_apply_enabled: boolean;
  cover_letter_template: string;
  resume_path?: string;
  // Pipeline settings
  min_ats_score?: number;
  resume_template?: string;
  personalize_cover_letter?: boolean;
  skip_application_form?: boolean;
  // Job preferences
  target_roles?: string;
  target_locations?: string;
  min_salary?: number;
  max_commute?: number;
  remote_only?: boolean;
  exclude_contract?: boolean;
  preferred_sponsorship?: string;
  years_experience?: number;
  job_preferences?: {
    roles?: string[];
    locations?: string[];
    remote_only?: boolean;
    min_salary?: number;
  };
}

export interface LlmProvider {
  provider: string;
  model: string;
  configured: boolean;
  is_primary: boolean;
}
