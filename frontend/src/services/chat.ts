
export type ChatSource = {
  chunk_id: string;
  document_id: string;
  similarity: number;
  snippet: string;
};

export type StreamHandlers = {
  onSources?: (s: ChatSource[]) => void;
  onToken?: (t: string) => void;
  onDone?: (reason: string) => void;
  onError?: (msg: string) => void;
};

export async function streamChat(
  message: string,
  token: string,
  handlers: StreamHandlers,
  opts: { documentIds?: string[]; k?: number; signal?: AbortSignal } = {},
) {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      document_ids: opts.documentIds ?? [],
      k: opts.k ?? 6,
    }),
    signal: opts.signal,
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

    // SSE messages are separated by a blank line
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
      const payload = JSON.parse(dataLine);

      if (event === "sources") handlers.onSources?.(payload.sources);
      else if (event === "token") handlers.onToken?.(payload.text);
      else if (event === "done") handlers.onDone?.(payload.reason);
      else if (event === "error") handlers.onError?.(payload.message);
    }
  }
}
