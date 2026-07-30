import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApiError, apiDelete, apiGet, apiPatchJson, apiPostJson } from "../api/client";
import type { EpicProgress, Ticket, TicketPriority, TicketStatus } from "../api/types";

const STATUSES: TicketStatus[] = ["backlog", "todo", "in_progress", "in_review", "done"];
const PRIORITIES: TicketPriority[] = ["low", "medium", "high", "urgent"];

// Single-user local dev tool -- no login, so "assign to me" just means this.
const CURRENT_USER = "carson";

function fieldLabel(field: string): string {
  return (
    { status: "Status", priority: "Priority", assignee: "Assignee", epic_id: "Epic", test_url: "Test link" }[field] ??
    field
  );
}

export function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [epics, setEpics] = useState<EpicProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [commentBody, setCommentBody] = useState("");
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [draft, setDraft] = useState({
    title: "",
    description: "",
    acceptance_criteria: "",
    test_url: "",
    labels: "",
  });

  useEffect(() => {
    apiGet<Ticket>(`/tickets/${id}`)
      .then(setTicket)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
    apiGet<EpicProgress[]>("/epics").then(setEpics).catch(() => {});
  }, [id]);

  async function patch(payload: Record<string, unknown>) {
    if (!ticket) return;
    try {
      const updated = await apiPatchJson<Ticket>(`/tickets/${ticket.id}`, payload);
      setTicket(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't update ticket");
    }
  }

  async function handleAddComment(event: FormEvent) {
    event.preventDefault();
    if (!ticket || !commentBody.trim()) return;
    setIsSubmittingComment(true);
    try {
      await apiPostJson(`/tickets/${ticket.id}/comments`, { body: commentBody.trim() });
      const refreshed = await apiGet<Ticket>(`/tickets/${ticket.id}`);
      setTicket(refreshed);
      setCommentBody("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't add comment");
    } finally {
      setIsSubmittingComment(false);
    }
  }

  function startEdit() {
    if (!ticket) return;
    setDraft({
      title: ticket.title,
      description: ticket.description ?? "",
      acceptance_criteria: ticket.acceptance_criteria ?? "",
      test_url: ticket.test_url ?? "",
      labels: ticket.labels.join(", "),
    });
    setIsEditing(true);
  }

  async function handleSaveEdit(event: FormEvent) {
    event.preventDefault();
    if (!ticket || !draft.title.trim() || !draft.acceptance_criteria.trim()) return;
    setIsSaving(true);
    try {
      const updated = await apiPatchJson<Ticket>(`/tickets/${ticket.id}`, {
        title: draft.title.trim(),
        description: draft.description.trim() || null,
        acceptance_criteria: draft.acceptance_criteria.trim(),
        test_url: draft.test_url.trim() || null,
        labels: draft.labels
          .split(",")
          .map((label) => label.trim())
          .filter(Boolean),
      });
      setTicket(updated);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save ticket");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    if (!ticket) return;
    await apiDelete(`/tickets/${ticket.id}`);
    navigate("/tickets");
  }

  if (error && !ticket) return <p role="alert">{error}</p>;
  if (!ticket) return <p>Loading...</p>;

  return (
    <div className="ticket-detail">
      <div className="ticket-detail-header">
        <span className="ticket-key">{ticket.key}</span>
        <div className="ticket-detail-header-actions">
          {!isEditing && (
            <button type="button" className="btn-ghost" onClick={startEdit}>
              Edit
            </button>
          )}
          <button type="button" className="btn-ghost" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>
      {!isEditing && <h1>{ticket.title}</h1>}
      {error && <p role="alert">{error}</p>}

      {isEditing && (
        <form className="ticket-edit-form" onSubmit={handleSaveEdit}>
          <label>
            Title
            <input
              type="text"
              value={draft.title}
              onChange={(e) => setDraft((d) => ({ ...d, title: e.target.value }))}
              required
              autoFocus
            />
          </label>
          <label>
            Description
            <textarea
              value={draft.description}
              onChange={(e) => setDraft((d) => ({ ...d, description: e.target.value }))}
              rows={4}
            />
          </label>
          <label>
            Acceptance criteria
            <textarea
              value={draft.acceptance_criteria}
              onChange={(e) => setDraft((d) => ({ ...d, acceptance_criteria: e.target.value }))}
              rows={4}
              required
            />
          </label>
          <label>
            Test URL
            <input
              type="url"
              placeholder="Where to try this feature, e.g. http://localhost:5173/recipes/1"
              value={draft.test_url}
              onChange={(e) => setDraft((d) => ({ ...d, test_url: e.target.value }))}
            />
          </label>
          <label>
            Labels
            <input
              type="text"
              placeholder="comma-separated, e.g. bug, frontend"
              value={draft.labels}
              onChange={(e) => setDraft((d) => ({ ...d, labels: e.target.value }))}
            />
          </label>
          <div className="ticket-edit-actions">
            <button type="submit" className="btn-primary" disabled={isSaving}>
              {isSaving ? "Saving..." : "Save"}
            </button>
            <button type="button" className="btn-ghost" onClick={() => setIsEditing(false)} disabled={isSaving}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="ticket-detail-fields">
        <label>
          Status
          <select value={ticket.status} onChange={(e) => patch({ status: e.target.value })}>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select value={ticket.priority} onChange={(e) => patch({ priority: e.target.value })}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Epic
          <select
            value={ticket.epic_id ?? ""}
            onChange={(e) => patch({ epic_id: e.target.value ? Number(e.target.value) : null })}
          >
            <option value="">No epic</option>
            {epics?.map((epic) => (
              <option key={epic.id} value={epic.id}>
                {epic.title}
              </option>
            ))}
          </select>
        </label>
        <div className="ticket-assignee-field">
          <span>Assignee: {ticket.assignee ?? "Unassigned"}</span>
          {ticket.assignee === CURRENT_USER ? (
            <button type="button" className="btn-ghost" onClick={() => patch({ assignee: null })}>
              Unassign
            </button>
          ) : (
            <button type="button" className="btn-ghost" onClick={() => patch({ assignee: CURRENT_USER })}>
              Assign to me
            </button>
          )}
        </div>
      </div>

      <p className="ticket-reporter">Reported by {ticket.reporter}</p>

      {!isEditing && (
        <>
          <p className="ticket-test-link">
            {ticket.test_url ? (
              <a href={ticket.test_url} target="_blank" rel="noreferrer">
                Test this feature ↗
              </a>
            ) : (
              <span className="ticket-empty">No test link yet — add one via Edit.</span>
            )}
          </p>

          {ticket.labels.length > 0 && (
            <div className="ticket-card-labels">
              {ticket.labels.map((label) => (
                <span key={label} className="ticket-label">
                  {label}
                </span>
              ))}
            </div>
          )}

          <h2>Description</h2>
          <p className="ticket-description">{ticket.description || "No description."}</p>

          <h2>Acceptance criteria</h2>
          <p className="ticket-acceptance-criteria">
            {ticket.acceptance_criteria || "None recorded (pre-dates the acceptance-criteria requirement)."}
          </p>
        </>
      )}

      <h2>Comments</h2>
      <ul className="ticket-comment-list">
        {ticket.comments.length === 0 && <li className="ticket-empty">No comments yet.</li>}
        {ticket.comments.map((comment) => (
          <li key={comment.id} className="ticket-comment-row">
            <span className="ticket-comment-author">{comment.author}</span>
            <p>{comment.body}</p>
          </li>
        ))}
      </ul>
      <form className="ticket-comment-form" onSubmit={handleAddComment}>
        <textarea
          value={commentBody}
          onChange={(e) => setCommentBody(e.target.value)}
          rows={3}
          placeholder="Add a comment..."
        />
        <button type="submit" className="btn-primary" disabled={isSubmittingComment}>
          {isSubmittingComment ? "Posting..." : "Comment"}
        </button>
      </form>

      <h2>Activity</h2>
      <ul className="ticket-activity-list">
        {ticket.activity.length === 0 && <li className="ticket-empty">No activity yet.</li>}
        {ticket.activity.map((entry) => (
          <li key={entry.id} className="ticket-activity-row">
            {entry.actor} changed {fieldLabel(entry.field)} from{" "}
            <strong>{entry.old_value ?? "none"}</strong> to <strong>{entry.new_value ?? "none"}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
