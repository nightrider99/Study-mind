import { useState } from "react";
import { Link } from "react-router-dom";
import { useAsync } from "../hooks/useAsync";
import { quizzesApi } from "../services/quizzes";
import { documentsApi } from "../services/documents";
import { notesApi } from "../services/notes";
import { Spinner } from "../components/common/Spinner";
import { Empty } from "../components/common/Empty";
import { ErrorBanner } from "../components/common/ErrorBanner";
import { useToast } from "../hooks/useToast";

export default function QuizPage() {
  const quizzes = useAsync(() => quizzesApi.list(), []);
  const docs = useAsync(() => documentsApi.list(), []);
  const notes = useAsync(() => notesApi.list(), []);
  const [num, setNum] = useState(10);
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [selectedNotes, setSelectedNotes] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [genErr, setGenErr] = useState<Error | null>(null);
  const { push } = useToast();

  async function generate() {
    if (!selectedDocs.length && !selectedNotes.length) {
      push("error", "Pick at least one document or note.");
      return;
    }
    setGenerating(true);
    setGenErr(null);
    try {
      const quiz = await quizzesApi.generate({
        document_ids: selectedDocs, note_ids: selectedNotes,
        num_questions: num, difficulty,
      });
      quizzes.reload();
      push("success", `Generated "${quiz.title}" with ${quiz.questions.length} questions.`);
      setSelectedDocs([]); setSelectedNotes([]);
    } catch (e) {
      setGenErr(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setGenerating(false);
    }
  }

  return (
    <>
      <div className="page-head"><h1>Quizzes</h1></div>
      <ErrorBanner error={quizzes.error ?? genErr} />

      <div className="card" style={{ marginBottom: 24 }}>
        <strong>Generate a new quiz</strong>
        <div className="grid cols-3" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Questions</label>
            <input className="input" type="number" min={3} max={30}
              value={num} onChange={(e) => setNum(Number(e.target.value))} />
          </div>
          <div className="field">
            <label>Difficulty</label>
            <select className="select" value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as any)}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>
        <div className="grid cols-2" style={{ marginTop: 8 }}>
          <div className="field">
            <label>Documents (multi-select)</label>
            <select className="select" multiple size={4} value={selectedDocs}
              onChange={(e) => setSelectedDocs(Array.from(e.target.selectedOptions).map((o) => o.value))}>
              {(docs.data ?? []).filter((d) => d.status === "ready").map((d) => (
                <option key={d.id} value={d.id}>{d.filename}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Notes (multi-select)</label>
            <select className="select" multiple size={4} value={selectedNotes}
              onChange={(e) => setSelectedNotes(Array.from(e.target.selectedOptions).map((o) => o.value))}>
              {(notes.data ?? []).map((n) => <option key={n.id} value={n.id}>{n.title}</option>)}
            </select>
          </div>
        </div>
        <div className="row" style={{ justifyContent: "flex-end", marginTop: 8 }}>
          <button className="btn primary" disabled={generating} onClick={generate}>
            {generating ? <span className="spinner" /> : null}
            {generating ? "Generating…" : "Generate quiz"}
          </button>
        </div>
      </div>

      {quizzes.loading ? <Spinner /> : !quizzes.data?.length ? (
        <Empty>No quizzes yet. Generate one above.</Empty>
      ) : (
        <div className="grid cols-3">
          {quizzes.data.map((q) => (
            <Link key={q.id} to={`/quiz/${q.id}`} className="card" style={{ color: "inherit", textDecoration: "none" }}>
              <div className="spread">
                <strong>{q.title}</strong>
                <span className="badge">{q.difficulty}</span>
              </div>
              <div className="muted" style={{ marginTop: 8, fontSize: 13 }}>
                {q.question_count} questions · {new Date(q.created_at).toLocaleDateString()}
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
