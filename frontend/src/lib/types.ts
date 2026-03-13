// ── Personas ──────────────────────────────

export interface Palette {
  primary: string;
  accent1: string;
  accent2: string;
  text_color: string;
  bg_color: string;
}

export interface FontStyle {
  size: number;
  weight: string;
  shadow: boolean;
  position: "center" | "top_third" | "bottom_third";
}

export interface Persona {
  id: string;
  name: string;
  description: string | null;
  prompt_image_base: string;
  prompt_image_variations: string[];
  prompt_video: string;
  negative_prompt: string;
  palette: Palette;
  font_family: string;
  font_style: FontStyle;
  style_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonaListItem {
  id: string;
  name: string;
  description: string | null;
  palette: Palette;
  font_family: string;
  created_at: string;
  updated_at: string;
  job_count: number;
}

export interface PersonaCreate {
  name: string;
  description?: string;
  prompt_image_base: string;
  prompt_image_variations?: string[];
  prompt_video: string;
  negative_prompt?: string;
  palette?: Palette;
  font_family?: string;
  font_style?: FontStyle;
  style_notes?: string;
}

// ── Jobs ──────────────────────────────────

export interface AssetInfo {
  url: string;
  type: string;
}

export interface JobAssets {
  trend?: AssetInfo;
  image?: AssetInfo;
  video_raw?: AssetInfo;
  video_final?: AssetInfo;
}

export interface JobTimeline {
  created?: string;
  trend_ready?: string;
  image_ready?: string;
  video_ready?: string;
  complete?: string;
}

export interface JobMetadata {
  image_seed?: number;
  video_duration?: number;
  generation_cost_usd?: number;
  total_time_seconds?: number;
}

export interface JobListItem {
  id: string;
  persona_id: string;
  persona_name: string;
  type: string;
  status: "pending" | "running" | "done" | "failed" | "cancelled";
  current_step: string | null;
  hook_text: string;
  created_at: string;
  updated_at: string;
}

export interface JobDetail {
  id: string;
  persona_id: string;
  persona_name: string;
  type: string;
  status: "pending" | "running" | "done" | "failed" | "cancelled";
  current_step: string | null;
  hook_text: string;
  trend_url: string | null;
  assets: JobAssets;
  timeline: JobTimeline;
  metadata: JobMetadata;
  error_message: string | null;
  celery_task_id: string | null;
  created_at: string;
  updated_at: string;
}

// ── Batch ─────────────────────────────────

export interface BatchDetail {
  id: string;
  persona_id: string;
  total: number;
  completed: number;
  failed: number;
  running: number;
  status: string;
  jobs: JobListItem[];
}

// ── Library ───────────────────────────────

export interface LibraryItem {
  id: string;
  job_id: string;
  persona_id: string;
  persona_name: string;
  hook_text: string;
  public_url: string;
  file_size: number | null;
  mime_type: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ── API Responses ─────────────────────────

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface PersonaListResponse {
  data: PersonaListItem[];
  total: number;
}

export interface GenerateSingleResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface GenerateBatchResponse {
  batch_id: string;
  job_ids: string[];
  total: number;
  status: string;
}

export interface MessageResponse {
  message: string;
}

export interface ApiErrorBody {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
