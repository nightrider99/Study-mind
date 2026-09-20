import type { ReactNode } from "react";

export function Empty({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="empty">
      <div style={{ marginBottom: action ? 16 : 0 }}>{children}</div>
      {action}
    </div>
  );
}
