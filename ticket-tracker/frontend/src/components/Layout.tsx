import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <header className="app-nav">
        <Link to="/tickets" className="app-nav-brand">
          Pantry Tickets
        </Link>
        <nav className="app-nav-links">
          <NavLink
            to="/tickets"
            className={({ isActive }) => (isActive ? "app-nav-link active" : "app-nav-link")}
          >
            Tickets
          </NavLink>
          <NavLink
            to="/epics"
            className={({ isActive }) => (isActive ? "app-nav-link active" : "app-nav-link")}
          >
            Epics
          </NavLink>
        </nav>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}
