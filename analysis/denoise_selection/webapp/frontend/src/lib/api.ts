import axios from "axios";
import type {
  MetricsPayload,
  PlotsPayload,
  ProcessRequest,
  TaskItem,
  TaskStatusResponse,
  UploadResponse,
} from "../types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
});

export async function uploadAudio(file: File): Promise<UploadResponse> {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await api.post<UploadResponse>("/api/upload", fd);
  return data;
}

export async function startProcess(req: ProcessRequest): Promise<{ ok: boolean; task_id: string; status: string; message: string }> {
  const { data } = await api.post("/api/process", req);
  return data;
}

export async function getTask(taskId: string): Promise<TaskStatusResponse> {
  const { data } = await api.get<TaskStatusResponse>(`/api/task/${taskId}`);
  return data;
}

export async function getMetrics(taskId: string): Promise<MetricsPayload> {
  const { data } = await api.get<{ ok: boolean; metrics: MetricsPayload }>(`/api/result/${taskId}/metrics`);
  return data.metrics;
}

export async function getPlots(taskId: string): Promise<PlotsPayload> {
  const { data } = await api.get<{ ok: boolean; plots: PlotsPayload }>(`/api/result/${taskId}/plots`);
  return data.plots;
}

export async function getHistory(): Promise<TaskItem[]> {
  const { data } = await api.get<{ ok: boolean; items: TaskItem[] }>("/api/history");
  return data.items;
}

export async function deleteTask(taskId: string): Promise<void> {
  await api.delete(`/api/history/${taskId}`);
}

export async function postAbx(taskId: string, x_is: string, guess: string): Promise<{ accuracy: number; total: number; correct: number }> {
  const { data } = await api.post(`/api/abx/${taskId}/record`, { x_is, guess });
  return data.stats;
}

export async function getAbxStats(taskId: string): Promise<{ accuracy: number; total: number; correct: number }> {
  const { data } = await api.get(`/api/abx/${taskId}/stats`);
  return data.stats;
}

export async function addBookmark(taskId: string, time_sec: number, note: string): Promise<void> {
  await api.post(`/api/bookmark/${taskId}`, { time_sec, note });
}

export function audioUrl(taskId: string, kind: "original" | "denoised" | "residual"): string {
  return `${api.defaults.baseURL}/api/result/${taskId}/audio/${kind}`;
}

