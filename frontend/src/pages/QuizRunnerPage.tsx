import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { quizzesApi } from "../services/quizzes";
import { Spinner } from "../components/common/Spinner";
import { ErrorBanner } from "../components/common/ErrorBanner";
import type { QuizDetail, QuizResult } from "../types";

export default function QuizRunnerPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const nav = useNavigate();
  const [quiz, setQuiz] = useState<QuizDetail | null>(null);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [err, setErr] = useState<Error | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!quizId) return;
    quizzesApi.get(quizId)
      .then((q) => { setQuiz(q); setAnswers(new Array(q.questions.length).fill(-1)); })
      .catch((e) => setErr(e instanceof Error ? e : new Error(String(e))));
  }, [quizId]);

  if (err) return <ErrorBanner error={err} />;
  if (!quiz) return <Spinner />;

  const q = quiz.questions[idx];
  const isLast = idx === quiz.questions.length - 1;

  async function submit() {
    if (!quizId || !quiz) return;
    if (answers.some((a) => a === -1)) {
      if (!confirm("Some questions are unanswered. Submit anyway?")) return;
    }
    setBusy(true);
    try {
      const r = await quizzesApi.submit(quizId, answers);
      setResult(r);
    } catch (e) {
      setErr(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <>
        <div className="page-head">
          <h1>{quiz.title} — Results</h1>
          <Link to="/quiz" className="btn">Back to quizzes</Link>
        </div>
        <div className="card" style={{ marginBottom: 20, textAlign: "center" }}>
          <div className="muted">Score</div>
          <div style={{ fontSize: 44, fontWeight: 700 }}>
            {result.score} / {result.total}
          </div>
          <div className="muted">{((result.score / result.total) * 100).toFixed(0)}%</div>
        </div>
        <div className="stack">
          {quiz.questions.map((qq, i) => {
            const correct = result.correct_indices[i];
            const chosen = answers[i];
            return (
              <div key={qq.id} className="card">
                <div className="spread" style={{ marginBottom: 8 }}>
                  <strong>Q{i + 1}. {qq.question}</strong>
                  <span className={`badge ${chosen === correct ? "success" : "danger"}`}>
                    {chosen === correct ? "Correct" : "Wrong"}
                  </span>
                </div>
                {qq.options.map((opt, j) => (
                  <div key={j}
                    className={`q-option ${j === correct ? "correct" : j === chosen ? "wrong" : ""}`}
                    style={{ cursor: "default" }}>
                    <span className="muted">{String.fromCharCode(65 + j)}.</span>
                    <span>{opt}</span>
                  </div>
                ))}
                {result.explanations[i] && (
                  <div className="muted" style={{ marginTop: 8, fontSize: 13 }}>
                    {result.explanations[i]}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </>
    );
  }

  return (
    <>
      <div className="page-head">
        <h1>{quiz.title}</h1>
        <span className="muted">{idx + 1} / {quiz.questions.length}</span>
      </div>

      <div className="card">
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
          {q.question}
        </div>
        {q.options.map((opt, j) => (
          <div key={j}
            className={`q-option ${answers[idx] === j ? "selected" : ""}`}
            onClick={() => setAnswers((a) => { const c = [...a]; c[idx] = j; return c; })}>
            <span className="muted">{String.fromCharCode(65 + j)}.</span>
            <span>{opt}</span>
          </div>
        ))}

        <div className="spread" style={{ marginTop: 20 }}>
          <button className="btn" disabled={idx === 0} onClick={() => setIdx((i) => i - 1)}>← Previous</button>
          {isLast
            ? <button className="btn primary" onClick={submit} disabled={busy}>
                {busy ? <span className="spinner" /> : null} Submit
              </button>
            : <button className="btn primary" onClick={() => setIdx((i) => i + 1)}>Next →</button>}
        </div>
      </div>
    </>
  );
}
