export type TaskStatus = "uploaded" | "queued" | "processing" | "completed" | "failed";

export interface UploadResponse {
  ok: boolean;
  task_id: string;
  filename: string;
  status: TaskStatus;
}

export interface ProcessRequest {
  task_id: string;
  method: string;
  run_distill_refine: boolean;
  deepfilter_model_dir?: string;
  noisereduce_strength: number;
}

export interface TaskStatusResponse {
  ok: boolean;
  task_id: string;
  status: TaskStatus;
  progress: number;
  message?: string;
  error?: string;
}

export interface TaskItem {
  task_id: string;
  filename: string;
  status: TaskStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  settings: Record<string, unknown>;
  paths: Record<string, string | null>;
  bookmarks: { time_sec: number; note: string }[];
  route?: string[];
  reason?: string;
}

export interface MetricsPayload {
  sample_rate: number;
  length_sec: number;
  method: string;
  route: string[];
  reason?: string;
  rms: Record<string, number>;
  snr_db: Record<string, number>;
  residual_stats: Record<string, number>;
}

export interface PlotItem {
  id: string;
  title: string;
  figure: { data: unknown[]; layout: Record<string, unknown> };
}

export interface PlotGroup {
  group: string;
  title: string;
  plots: PlotItem[];
}

export interface PlotsPayload {
  groups: PlotGroup[];
}

