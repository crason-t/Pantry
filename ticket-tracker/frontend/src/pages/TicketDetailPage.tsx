import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApiError, apiDelete, apiGet, apiPatchJson, apiPostJson } from "../api/client";
import type { EpicProgress, Ticket, TicketPriority, TicketStatus } from "../api/types";

const STATUSES: TicketStatus[] = ["backlog", "todo", "in_progress", "in_review", "done"];
const PRIORITIES: TicketPriority[] = ["low", "medium", "high", "urgent"];

// Single-user local dev tool -- no login, so "assign to me" just means this.
const CURRENT_USER = "carson";

function fieldLabel(field: string): string {
  return { status: "Status", priority: "Priority", assignee: "Assignee", epic_id: "Epic" }[field] ?? field;
}

export function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [epics, setEpics] = useState<EpicProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [commentBody, setCommentBody] = useState("");
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);

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
        <button type="button" className="btn-ghost" onClick={handleDelete}>
          Delete
        </button>
      </div>
      <h1>{ticket.title}</h1>
      {error && <p role="alert">{error}</p>}

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

      <h2>Description</h2>
      <p className="ticket-description">{ticket.description || "No description."}</p>

      <h2>Acceptance criteria</h2>
      <p className="ticket-acceptance-criteria">
        {ticket.acceptance_criteria || "None recorded (pre-dates the acceptance-criteria requirement)."}
      </p>

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
