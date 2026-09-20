import { apiFetch } from "./api";
import { supabase } from "./supabase";
import type { ChatSession, ChatMessage, ChatSource } from "../types";

const BASE = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

export type StreamHandlers = {
  onSession?: (sessionId: string) => void;
  onSources?: (sources: ChatSource[]) => void;
  onToken?: (text: string) => void;
  onDone?: (reason: string) => void;
  onError?: (message: string) => void;
};

export const chatApi = {
  listSessions: () => apiFetch<ChatSession[]>("/api/v1/chat/sessions"),
  getSession: (id: string) => apiFetch<ChatSession & { messages: ChatMessage[] }>(`/api/v1/chat/sessions/${id}`),
  deleteSession: (id: string) => apiFetch<void>(`/api/v1/chat/sessions/${id}`, { method: "DELETE" }),

  async stream(
    body: { message: string; session_id?: string | null; document_ids?: string[]; k?: number },
    handlers: StreamHandlers,
    signal?: AbortSignal
  ): Promise<void> {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;

    const res = await fetch(`${BASE}/api/v1/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      signal,
    });

    if (!res.ok || !res.body) {
      handlers.onError?.(`HTTP ${res.status}`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let idx: number;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const raw = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);

        let event = "message";
        let dataLine = "";
        for (const line of raw.split("\n")) {
          if (line.startsWith("event: ")) event = line.slice(7).trim();
          else if (line.startsWith("data: ")) dataLine += line.slice(6);
        }
        if (!dataLine) continue;
        let payload: any;
        try { payload = JSON.parse(dataLine); } catch { continue; }

        if (event === "session") handlers.onSession?.(payload.session_id);
        else if (event === "sources") handlers.onSources?.(payload.sources);
        else if (event === "token") handlers.onToken?.(payload.text);
        else if (event === "done") handlers.onDone?.(payload.reason);
        else if (event === "error") handlers.onError?.(payload.message);
      }
    }
  },
};
