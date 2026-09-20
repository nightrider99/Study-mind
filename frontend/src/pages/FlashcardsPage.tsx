import { useState } from "react";
import { Link } from "react-router-dom";
import { useAsync } from "../hooks/useAsync";
import { flashcardsApi } from "../services/flashcards";
import { documentsApi } from "../services/documents";
import { notesApi } from "../services/notes";
import { Spinner } from "../components/common/Spinner";
import { Empty } from "../components/common/Empty";
import { ErrorBanner } from "../components/common/ErrorBanner";
import { useToast } from "../hooks/useToast";

export default function FlashcardsPage() {
  const decks = useAsync(() => flashcardsApi.listDecks(), []);
  const docs = useAsync(() => documentsApi.list(), []);
  const notes = useAsync(() => notesApi.list(), []);
  const [num, setNum] = useState(15);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [selectedNotes, setSelectedNotes] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<Error | null>(null);
  const { push } = useToast();

  async function generate() {
    if (!selectedDocs.length && !selectedNotes.length) {
      push("error", "Pick at least one document or note.");
      return;
    }
    setBusy(true); setErr(null);
    try {
      const deck = await flashcardsApi.generate({
        document_ids: selectedDocs, note_ids: selectedNotes, num_cards: num,
      });
      decks.reload();
      push("success", `Created deck "${deck.title}" with ${deck.cards.length} cards.`);
      setSelectedDocs([]); setSelectedNotes([]);
    } catch (e) {
      setErr(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-head"><h1>Flashcards</h1></div>
      <ErrorBanner error={decks.error ?? err} />

      <div className="card" style={{ marginBottom: 24 }}>
        <strong>Generate a deck</strong>
        <div className="grid cols-3" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Cards</label>
            <input className="input" type="number" min={3} max={50}
              value={num} onChange={(e) => setNum(Number(e.target.value))} />
          </div>
        </div>
        <div className="grid cols-2">
          <div className="field">
            <label>Documents</label>
            <select className="select" multiple size={4} value={selectedDocs}
              onChange={(e) => setSelectedDocs(Array.from(e.target.selectedOptions).map((o) => o.value))}>
              {(docs.data ?? []).filter((d) => d.status === "ready").map((d) => (
                <option key={d.id} value={d.id}>{d.filename}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Notes</label>
            <select className="select" multiple size={4} value={selectedNotes}
              onChange={(e) => setSelectedNotes(Array.from(e.target.selectedOptions).map((o) => o.value))}>
              {(notes.data ?? []).map((n) => <option key={n.id} value={n.id}>{n.title}</option>)}
            </select>
          </div>
        </div>
        <div className="row" style={{ justifyContent: "flex-end" }}>
          <button className="btn primary" disabled={busy} onClick={generate}>
            {busy ? <span className="spinner" /> : null}
            {busy ? "Generating…" : "Generate deck"}
          </button>
        </div>
      </div>

      {decks.loading ? <Spinner /> : !decks.data?.length ? (
        <Empty>No decks yet. Generate one above.</Empty>
      ) : (
        <div className="grid cols-3">
          {decks.data.map((d) => (
            <Link key={d.id} to={`/flashcards/${d.id}`} className="card" style={{ color: "inherit", textDecoration: "none" }}>
              <strong>{d.title}</strong>
              <div className="muted" style={{ marginTop: 8, fontSize: 13 }}>
                {d.card_count} cards
                {d.due_count > 0 && <span className="badge warn" style={{ marginLeft: 8 }}>{d.due_count} due</span>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
