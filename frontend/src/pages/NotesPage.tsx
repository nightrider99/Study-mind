import { useState } from "react";
import { useAsync } from "../hooks/useAsync";
import { notesApi } from "../services/notes";
import { documentsApi } from "../services/documents";
import { Spinner } from "../components/common/Spinner";
import { Empty } from "../components/common/Empty";
import { ErrorBanner } from "../components/common/ErrorBanner";
import { Modal } from "../components/common/Modal";
import { useToast } from "../hooks/useToast";
import type { Note } from "../types";

export default function NotesPage() {
  const { data, loading, error, reload } = useAsync(() => notesApi.list(), []);
  const [editing, setEditing] = useState<Note | "new" | null>(null);
  const [uploadErr, setUploadErr] = useState<Error | null>(null);
  const [uploading, setUploading] = useState(false);
  const { push } = useToast();

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadErr(null);
    try {
      await documentsApi.upload(file);
      push("success", "Document uploaded and indexed.");
    } catch (err) {
      setUploadErr(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function del(id: string) {
    if (!confirm("Delete this note?")) return;
    try {
      await notesApi.remove(id);
      reload();
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>Notes</h1>
        <div className="row wrap">
          <label className="btn">
            {uploading ? <span className="spinner" /> : null}
            Upload PDF
            <input type="file" accept="application/pdf" style={{ display: "none" }}
              onChange={upload} disabled={uploading} />
          </label>
          <button className="btn primary" onClick={() => setEditing("new")}>New note</button>
        </div>
      </div>

      <ErrorBanner error={error ?? uploadErr} />
      {loading ? <Spinner /> : !data?.length ? (
        <Empty action={<button className="btn primary" onClick={() => setEditing("new")}>Create your first note</button>}>
          No notes yet.
        </Empty>
      ) : (
        <div className="grid cols-3">
          {data.map((n) => (
            <div key={n.id} className="card" style={{ cursor: "pointer", display: "flex", flexDirection: "column", gap: 8 }}
              onClick={() => setEditing(n)}>
              <div className="spread">
                <strong style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.title}</strong>
              </div>
              <div className="muted" style={{ fontSize: 13, height: 60, overflow: "hidden" }}>
                {n.content.slice(0, 200) || "Empty"}
              </div>
              <div className="spread">
                <span className="muted" style={{ fontSize: 12 }}>{new Date(n.updated_at).toLocaleDateString()}</span>
                <button className="btn ghost sm" onClick={(e) => { e.stopPropagation(); del(n.id); }}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <NoteEditor
        editing={editing}
        onClose={() => setEditing(null)}
        onSaved={() => { setEditing(null); reload(); }}
      />
    </>
  );
}

function NoteEditor({
  editing, onClose, onSaved,
}: { editing: Note | "new" | null; onClose: () => void; onSaved: () => void }) {
  const isNew = editing === "new";
  const note = editing && editing !== "new" ? editing : null;
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<Error | null>(null);

  // reset when modal opens
  if (editing && isNew && (title !== "" || content !== "") && !busy && !err) { /* noop */ }

  // use a key on modal to remount — simpler:
  return (
    <Modal key={isNew ? "new" : note?.id ?? "none"} open={!!editing} onClose={onClose}
      title={isNew ? "New note" : "Edit note"}>
      <NoteEditorInner
        initial={note ?? { title: "", content: "" }}
        busy={busy}
        err={err}
        onSubmit={async (t, c) => {
          setBusy(true); setErr(null);
          try {
            if (isNew) await notesApi.create({ title: t, content: c });
            else if (note) await notesApi.update(note.id, { title: t, content: c });
            onSaved();
          } catch (e) {
            setErr(e instanceof Error ? e : new Error(String(e)));
          } finally {
            setBusy(false);
          }
        }}
      />
    </Modal>
  );
}

function NoteEditorInner({
  initial, busy, err, onSubmit,
}: { initial: { title: string; content: string }; busy: boolean; err: Error | null; onSubmit: (t: string, c: string) => void }) {
  const [title, setTitle] = useState(initial.title);
  const [content, setContent] = useState(initial.content);

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(title, content); }}>
      <ErrorBanner error={err} />
      <div className="field">
        <label>Title</label>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </div>
      <div className="field">
        <label>Content</label>
        <textarea className="textarea" style={{ minHeight: 260 }}
          value={content} onChange={(e) => setContent(e.target.value)} />
      </div>
      <div className="row" style={{ justifyContent: "flex-end" }}>
        <button className="btn primary" disabled={busy}>
          {busy ? <span className="spinner" /> : null} Save
        </button>
      </div>
    </form>
  );
}
