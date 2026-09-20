export function Spinner({ label }: { label?: string }) {
  return (
    <div className="row" style={{ justifyContent: "center", padding: 32, color: "var(--muted)" }}>
      <span className="spinner" /> {label ?? "Loading…"}
    </div>
  );
}
