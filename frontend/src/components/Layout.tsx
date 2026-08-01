import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-nav">
        <Link to="/" className="app-nav-brand">
          Pantry
        </Link>
        <nav className="app-nav-links">
          <NavLink
            to="/cookbook"
            className={({ isActive }) => (isActive ? "app-nav-link active" : "app-nav-link")}
          >
            Cookbook
          </NavLink>
        </nav>
        <div className="app-nav-actions">
          <Link to="/recipes/new" className="btn-primary">
            + New recipe
          </Link>
          {user && <span className="app-nav-user">{user.email}</span>}
          <button type="button" className="btn-ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}
