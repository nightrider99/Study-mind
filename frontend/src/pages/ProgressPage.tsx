import { useAsync } from "../hooks/useAsync";
import { progressApi } from "../services/progress";
import { Spinner } from "../components/common/Spinner";
import { ErrorBanner } from "../components/common/ErrorBanner";

export default function ProgressPage() {
  const summary = useAsync(() => progressApi.summary(), []);
  const timeline = useAsync(() => progressApi.timeline(30), []);

  if (summary.loading) return <Spinner />;

  const max = Math.max(1, ...(timeline.data?.days ?? []).map((d) => d.quiz_attempts + d.cards_reviewed));

  return (
    <>
      <div className="page-head"><h1>Progress</h1></div>
      <ErrorBanner error={summary.error ?? timeline.error} />

      <div className="grid cols-4" style={{ marginBottom: 24 }}>
        <Stat label="Streak" value={`${summary.data?.streak_days ?? 0}d`} />
        <Stat label="Quizzes taken" value={`${summary.data?.quizzes_taken ?? 0}`} />
        <Stat label="Avg score" value={`${(summary.data?.avg_score ?? 0).toFixed(1)}%`} />
        <Stat label="Cards due" value={`${summary.data?.cards_due ?? 0} / ${summary.data?.cards_total ?? 0}`} />
      </div>

      <div className="card">
        <strong>Last 30 days</strong>
        <div className="muted" style={{ fontSize: 13, marginBottom: 16 }}>
          Bars show quizzes + cards reviewed per day
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 180 }}>
          {(timeline.data?.days ?? []).map((d) => {
            const total = d.quiz_attempts + d.cards_reviewed;
            const h = Math.round((total / max) * 160);
            return (
              <div key={d.day} title={`${d.day}: ${d.quiz_attempts} quizzes, ${d.cards_reviewed} cards`}
                style={{
                  flex: 1, height: Math.max(2, h),
                  background: total > 0 ? "var(--accent)" : "var(--border)",
                  borderRadius: 3, minWidth: 4,
                }} />
            );
          })}
        </div>
        <div className="spread muted" style={{ fontSize: 11, marginTop: 6 }}>
          <span>{timeline.data?.days?.[0]?.day}</span>
          <span>{timeline.data?.days?.at(-1)?.day}</span>
        </div>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <div className="muted" style={{ fontSize: 13, marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: "-0.02em" }}>{value}</div>
    </div>
  );
}
