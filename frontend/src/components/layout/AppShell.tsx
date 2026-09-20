import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/notes", label: "Notes" },
  { to: "/chat", label: "Chat" },
  { to: "/quiz", label: "Quizzes" },
  { to: "/flashcards", label: "Flashcards" },
  { to: "/progress", label: "Progress" },
];

export function AppShell() {
  const { user, signOut } = useAuth();
  const nav = useNavigate();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Study<span>Mind</span></div>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            {l.label}
          </NavLink>
        ))}
        <div className="sidebar-footer">
          <div className="user-email" title={user?.email ?? ""}>{user?.email}</div>
          <button className="btn ghost sm" style={{ marginTop: 8, width: "100%" }}
            onClick={async () => { await signOut(); nav("/login"); }}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
