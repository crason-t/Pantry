import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiGet, apiPostJson } from "../api/client";
import type { EpicProgress } from "../api/types";

export function EpicsPage() {
  const [epics, setEpics] = useState<EpicProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showNewForm, setShowNewForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    apiGet<EpicProgress[]>("/epics")
      .then(setEpics)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!newTitle.trim()) return;
    setIsSubmitting(true);
    try {
      const created = await apiPostJson<EpicProgress>("/epics", { title: newTitle.trim() });
      setEpics((prev) => (prev ? [...prev, { ...created, ticket_count: 0, done_count: 0 }] : [created]));
      setNewTitle("");
      setShowNewForm(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="epics-page">
      <div className="tickets-header">
        <h1>Epics</h1>
        <button type="button" className="btn-primary" onClick={() => setShowNewForm((v) => !v)}>
          + New epic
        </button>
      </div>

      {error && <p role="alert">{error}</p>}

      {showNewForm && (
        <form className="ticket-new-form" onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Epic title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            autoFocus
            required
          />
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Adding..." : "Add"}
          </button>
        </form>
      )}

      {epics === null && !error && <p>Loading...</p>}
      {epics !== null && epics.length === 0 && <p>No epics yet.</p>}

      {epics !== null && epics.length > 0 && (
        <ul className="epic-list">
          {epics.map((epic) => {
            const pct = epic.ticket_count === 0 ? 0 : Math.round((epic.done_count / epic.ticket_count) * 100);
            return (
              <li key={epic.id} className="epic-row">
                <div className="epic-row-top">
                  <Link to={`/tickets?epic=${epic.id}`} className="epic-title">
                    {epic.title}
                  </Link>
                  <span className="epic-progress-label">
                    {epic.done_count}/{epic.ticket_count} done
                  </span>
                </div>
                <div className="epic-progress-track">
                  <div className="epic-progress-fill" style={{ width: `${pct}%` }} />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
