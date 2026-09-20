import { apiFetch } from "./api";
import type { ProgressSummary, TimelinePoint } from "../types";

export const progressApi = {
  summary: () => apiFetch<ProgressSummary>("/api/v1/progress/summary"),
  timeline: (days = 30) =>
    apiFetch<{ days: TimelinePoint[] }>(`/api/v1/progress/timeline?days=${days}`),
};
