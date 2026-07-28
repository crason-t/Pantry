import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function CookbookPage() {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Cookbook</h1>
      <p>Logged in as {user?.email}</p>
      <button type="button" onClick={logout}>
        Log out
      </button>
      <p>
        <Link to="/recipes/new">Ingest a recipe</Link>
      </p>
      <p>No saved recipes yet -- this is a placeholder for the recipe list.</p>
    </div>
  );
}
