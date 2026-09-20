import { Link } from "react-router-dom";
import { useAsync } from "../hooks/useAsync";
import { progressApi } from "../services/progress";
import { documentsApi } from "../services/documents";
import { notesApi } from "../services/notes";
import { Spinner } from "../components/common/Spinner";
import { ErrorBanner } from "../components/common/ErrorBanner";

export default function DashboardPage() {
  const summary = useAsync(() => progressApi.summary(), []);
  const recentNotes = useAsync(() => notesApi.list(), []);
  const recentDocs = useAsync(() => documentsApi.list(), []);

  if (summary.loading) return <Spinner />;

  return (
    <>
      <div className="page-head">
        <h1>Dashboard</h1>
      </div>
      <ErrorBanner error={summary.error ?? recentNotes.error ?? recentDocs.error} />

      <div className="grid cols-4" style={{ marginBottom: 24 }}>
        <Stat label="Study streak" value={`${summary.data?.streak_days ?? 0} day${summary.data?.streak_days === 1 ? "" : "s"}`} />
        <Stat label="Avg quiz score" value={`${summary.data?.avg_score?.toFixed(1) ?? "0"}%`} />
        <Stat label="Cards due" value={`${summary.data?.cards_due ?? 0}`} />
        <Stat label="Notes" value={`${summary.data?.notes_count ?? 0}`} />
      </div>

      <div className="grid cols-2">
        <div className="card">
          <div className="spread" style={{ marginBottom: 12 }}>
            <strong>Recent notes</strong>
            <Link to="/notes" className="muted">View all →</Link>
          </div>
          {(recentNotes.data ?? []).slice(0, 4).map((n) => (
            <div key={n.id} className="spread" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span>{n.title}</span>
              <span className="muted" style={{ fontSize: 12 }}>{new Date(n.updated_at).toLocaleDateString()}</span>
            </div>
          ))}
          {!recentNotes.data?.length && <div className="muted">No notes yet.</div>}
        </div>

        <div className="card">
          <div className="spread" style={{ marginBottom: 12 }}>
            <strong>Documents</strong>
            <Link to="/chat" className="muted">Upload →</Link>
          </div>
          {(recentDocs.data ?? []).slice(0, 4).map((d) => (
            <div key={d.id} className="spread" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 260 }}>{d.filename}</span>
              <span className={`badge ${d.status === "ready" ? "success" : d.status === "failed" ? "danger" : "warn"}`}>{d.status}</span>
            </div>
          ))}
          {!recentDocs.data?.length && <div className="muted">No documents yet.</div>}
        </div>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <div className="muted" style={{ fontSize: 13, marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em" }}>{value}</div>
    </div>
  );
}
