import { supabase } from "./supabase";

const BASE = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;
  detail?: unknown;

  constructor(code: string, message: string, status: number, detail?: unknown) {
    super(message);
    this.code = code;
    this.status = status;
    this.detail = detail;
  }
}

async function authHeader(): Promise<Record<string, string>> {
  // Fresh token every call — token refreshes after expiry without any client dance.
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string> | undefined),
    ...(await authHeader()),
  };
  if (init.body && !(init.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  const isJson =
    res.headers.get("content-type")?.includes("application/json") === true;
  const payload = isJson && text ? JSON.parse(text) : text;

  if (!res.ok) {
    const err = (payload as any)?.error;
    if (err?.code && err?.message) {
      throw new ApiError(err.code, err.message, res.status, err.detail);
    }
    // FastAPI default shape (validation, HTTPException)
    const msg = (payload as any)?.detail ?? `HTTP ${res.status}`;
    throw new ApiError(
      typeof msg === "string" ? "HTTP_ERROR" : "VALIDATION_ERROR",
      typeof msg === "string" ? msg : "Invalid request",
      res.status,
      typeof msg !== "string" ? msg : undefined
    );
  }

  return payload as T;
}
