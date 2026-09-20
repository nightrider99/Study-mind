import { apiFetch } from "./api";
import type { Document } from "../types";

export const documentsApi = {
  list: () => apiFetch<Document[]>("/api/v1/documents"),
  get: (id: string) => apiFetch<Document>(`/api/v1/documents/${id}`),
  upload: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return apiFetch<Document>("/api/v1/documents/upload", { method: "POST", body: fd });
  },
  remove: (id: string) => apiFetch<void>(`/api/v1/documents/${id}`, { method: "DELETE" }),
};
