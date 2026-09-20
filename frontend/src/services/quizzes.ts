import { apiFetch } from "./api";
import type { QuizSummary, QuizDetail, QuizResult } from "../types";

export const quizzesApi = {
  list: () => apiFetch<QuizSummary[]>("/api/v1/quizzes"),
  get: (id: string) => apiFetch<QuizDetail>(`/api/v1/quizzes/${id}`),
  generate: (body: {
    document_ids?: string[];
    note_ids?: string[];
    num_questions?: number;
    difficulty?: "easy" | "medium" | "hard";
    title?: string;
  }) => apiFetch<QuizDetail>("/api/v1/quizzes/generate", { method: "POST", body: JSON.stringify(body) }),
  submit: (id: string, answers: number[]) =>
    apiFetch<QuizResult>(`/api/v1/quizzes/${id}/submit`, { method: "POST", body: JSON.stringify({ answers }) }),
  remove: (id: string) => apiFetch<void>(`/api/v1/quizzes/${id}`, { method: "DELETE" }),
};
