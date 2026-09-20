import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { chatApi } from "../services/chat";
import { documentsApi } from "../services/documents";
import { useAsync } from "../hooks/useAsync";
import { useToast } from "../hooks/useToast";
import type { ChatSource } from "../types";

type Msg = { role: "user" | "assistant"; content: string; sources?: ChatSource[] };

export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const nav = useNavigate();
  const { push } = useToast();

  const sessions = useAsync(() => chatApi.listSessions(), []);
  const documents = useAsync(() => documentsApi.list(), []);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [docFilter, setDocFilter] = useState<string[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const readyDocs = useMemo(
    () => (documents.data ?? []).filter((d) => d.status === "ready"),
    [documents.data]
  );

  useEffect(() => {
    if (!sessionId) { setMessages([]); return; }
    chatApi.getSession(sessionId)
      .then((s) => setMessages(s.messages.map((m) => ({ role: m.role, content: m.content, sources: m.sources ?? undefined }))))
      .catch((e) => push("error", e instanceof Error ? e.message : "Failed to load session"));
  }, [sessionId, push]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setMessages((m) => [...m, { role: "assistant", content: "" }]);
    setStreaming(true);

    const ac = new AbortController();
    abortRef.current = ac;

    await chatApi.stream(
      { message: text, session_id: sessionId ?? null, document_ids: docFilter },
      {
        onSession: (sid) => {
          if (!sessionId) {
            nav(`/chat/${sid}`, { replace: true });
            sessions.reload();
          }
        },
        onSources: (s) => {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = { ...copy[copy.length - 1], sources: s };
            return copy;
          });
        },
        onToken: (t) => {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = { ...copy[copy.length - 1], content: copy[copy.length - 1].content + t };
            return copy;
          });
        },
        onError: (msg) => push("error", msg),
        onDone: () => setStreaming(false),
      },
      ac.signal
    );
    setStreaming(false);
  }

  function stop() {
    abortRef.current?.abort();
    setStreaming(false);
  }

  async function newChat() {
    nav("/chat");
  }

  async function deleteSession(id: string) {
    if (!confirm("Delete this conversation?")) return;
    try {
      await chatApi.deleteSession(id);
      sessions.reload();
      if (id === sessionId) nav("/chat");
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <div className="chat-shell">
      <aside className="chat-sidebar">
        <div style={{ padding: 12 }}>
          <button className="btn primary sm" style={{ width: "100%" }} onClick={newChat}>+ New chat</button>
        </div>
        {(sessions.data ?? []).map((s) => (
          <div key={s.id} className={`item ${s.id === sessionId ? "active" : ""}`}
            onClick={() => nav(`/chat/${s.id}`)}>
            <div className="spread">
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 160 }}>{s.title}</span>
              <button className="btn ghost sm" onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}>×</button>
            </div>
          </div>
        ))}
        {!sessions.data?.length && <div className="muted" style={{ padding: 14, fontSize: 13 }}>No chats yet.</div>}
      </aside>

      <section className="chat-main">
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }} className="row wrap">
          <span className="muted" style={{ fontSize: 13 }}>Sources:</span>
          <select className="select" style={{ maxWidth: 320, padding: "4px 8px", fontSize: 13 }}
            multiple size={1}
            value={docFilter}
            onChange={(e) => setDocFilter(Array.from(e.target.selectedOptions).map((o) => o.value))}>
            {readyDocs.length === 0 && <option disabled>No ready documents</option>}
            {readyDocs.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
          </select>
          {docFilter.length > 0 && (
            <button className="btn ghost sm" onClick={() => setDocFilter([])}>Clear filter</button>
          )}
          <span className="muted" style={{ fontSize: 12 }}>
            {docFilter.length ? `${docFilter.length} selected` : "all documents"}
          </span>
        </div>

        <div className="chat-messages" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="empty" style={{ margin: "auto" }}>
              Ask a question about your uploaded documents.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`}>
              {m.content || (streaming && i === messages.length - 1 ? <span className="spinner" /> : "")}
              {m.sources && m.sources.length > 0 && (
                <div className="chat-sources">
                  {m.sources.slice(0, 4).map((s, j) => (
                    <div key={j} title={s.snippet}>[{(j + 1)}] {(s.similarity * 100).toFixed(0)}% · {s.snippet.slice(0, 80)}…</div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="chat-input">
          <textarea className="textarea" style={{ minHeight: 44, maxHeight: 160 }}
            placeholder="Ask about your notes or documents…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
            }}
            disabled={streaming}
          />
          {streaming
            ? <button className="btn" onClick={stop}>Stop</button>
            : <button className="btn primary" onClick={send} disabled={!input.trim()}>Send</button>}
        </div>
      </section>
    </div>
  );
}
