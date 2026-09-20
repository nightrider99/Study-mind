import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ErrorBanner } from "../components/common/ErrorBanner";

export default function LoginPage() {
  const { user, loading, signIn, signUp, signInWithMagicLink } = useAuth();
  const nav = useNavigate();
  const loc = useLocation() as { state?: { from?: string } };
  const [mode, setMode] = useState<"signin" | "signup" | "magic">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<Error | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (loading) return null;
  if (user) return <Navigate to={loc.state?.from ?? "/"} replace />;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      if (mode === "signin") {
        await signIn(email, password);
        nav(loc.state?.from ?? "/", { replace: true });
      } else if (mode === "signup") {
        const { needsConfirmation } = await signUp(email, password);
        if (needsConfirmation) {
          setMsg("Check your email to confirm your account, then sign in.");
          setMode("signin");
        } else {
          nav("/", { replace: true });
        }
      } else {
        await signInWithMagicLink(email);
        setMsg("Magic link sent — check your email.");
      }
    } catch (e) {
      setErr(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }}>
      <div className="card" style={{ width: 400, maxWidth: "100%", padding: 28 }}>
        <div style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>
          Study<span style={{ color: "var(--accent)" }}>Mind</span>
        </div>
        <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
          Turn your notes into quizzes, flashcards, and answers.
        </p>

        {msg && <div className="banner success">{msg}</div>}
        <ErrorBanner error={err} />

        <form onSubmit={submit}>
          <div className="field">
            <label>Email</label>
            <input className="input" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
          </div>
          {mode !== "magic" && (
            <div className="field">
              <label>Password</label>
              <input className="input" type="password" value={password}
                onChange={(e) => setPassword(e.target.value)} required minLength={6}
                autoComplete={mode === "signin" ? "current-password" : "new-password"} />
            </div>
          )}
          <button className="btn primary" style={{ width: "100%" }} disabled={busy}>
            {busy ? <span className="spinner" /> : null}
            {mode === "signin" ? "Sign in" : mode === "signup" ? "Create account" : "Send magic link"}
          </button>
        </form>

        <div className="divider" />
        <div className="stack" style={{ gap: 8 }}>
          {mode !== "signin" && <button className="btn ghost sm" onClick={() => setMode("signin")}>Sign in instead</button>}
          {mode !== "signup" && <button className="btn ghost sm" onClick={() => setMode("signup")}>Create an account</button>}
          {mode !== "magic" && <button className="btn ghost sm" onClick={() => setMode("magic")}>Use magic link</button>}
        </div>
      </div>
    </div>
  );
}
