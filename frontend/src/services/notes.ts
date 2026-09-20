import { apiFetch } from "./api";
import type { Note } from "../types";

export const notesApi = {
  list: () => apiFetch<Note[]>("/api/v1/notes"),
  get: (id: string) => apiFetch<Note>(`/api/v1/notes/${id}`),
  create: (body: { title: string; content?: string; tags?: string[] }) =>
    apiFetch<Note>("/api/v1/notes", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<Pick<Note, "title" | "content" | "tags">>) =>
    apiFetch<Note>(`/api/v1/notes/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  remove: (id: string) => apiFetch<void>(`/api/v1/notes/${id}`, { method: "DELETE" }),
};
