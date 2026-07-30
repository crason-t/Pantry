import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { ApiError, apiGet, apiPatchJson, apiPostJson } from "../api/client";
import type { EpicProgress, TicketPriority, TicketStatus, TicketSummary } from "../api/types";
import { TicketCard } from "../components/TicketCard";

const COLUMNS: { status: TicketStatus; label: string }[] = [
  { status: "backlog", label: "Backlog" },
  { status: "todo", label: "To Do" },
  { status: "in_progress", label: "In Progress" },
  { status: "in_review", label: "In Review" },
  { status: "done", label: "Done" },
];

export function TicketsPage() {
  const [searchParams] = useSearchParams();
  const [tickets, setTickets] = useState<TicketSummary[] | null>(null);
  const [epics, setEpics] = useState<EpicProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [epicFilter, setEpicFilter] = useState<string>(searchParams.get("epic") ?? "all");
  const [showNewForm, setShowNewForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newAcceptanceCriteria, setNewAcceptanceCriteria] = useState("");
  const [newPriority, setNewPriority] = useState<TicketPriority>("medium");
  const [newEpicId, setNewEpicId] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [draggedId, setDraggedId] = useState<number | null>(null);

  useEffect(() => {
    apiGet<TicketSummary[]>("/tickets")
      .then(setTickets)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
    apiGet<EpicProgress[]>("/epics").then(setEpics).catch(() => {});
  }, []);

  const visibleTickets = useMemo(() => {
    if (!tickets) return [];
    if (epicFilter === "all") return tickets;
    if (epicFilter === "none") return tickets.filter((t) => t.epic_id === null);
    return tickets.filter((t) => t.epic_id === Number(epicFilter));
  }, [tickets, epicFilter]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!newTitle.trim() || !newAcceptanceCriteria.trim()) return;
    setIsSubmitting(true);
    try {
      const created = await apiPostJson<TicketSummary>("/tickets", {
        title: newTitle.trim(),
        acceptance_criteria: newAcceptanceCriteria.trim(),
        priority: newPriority,
        epic_id: newEpicId ? Number(newEpicId) : null,
      });
      setTickets((prev) => (prev ? [...prev, created] : [created]));
      setNewTitle("");
      setNewAcceptanceCriteria("");
      setNewPriority("medium");
      setNewEpicId("");
      setShowNewForm(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function moveTicket(ticketId: number, status: TicketStatus) {
    const current = tickets?.find((t) => t.id === ticketId);
    if (!current || current.status === status) return;

    setTickets((prev) => prev?.map((t) => (t.id === ticketId ? { ...t, status } : t)) ?? prev);
    try {
      await apiPatchJson<TicketSummary>(`/tickets/${ticketId}`, { status });
    } catch (err) {
      setTickets((prev) => prev?.map((t) => (t.id === ticketId ? { ...t, status: current.status } : t)) ?? prev);
      setError(err instanceof ApiError ? err.message : "Couldn't move ticket");
    }
  }

  return (
    <div className="tickets-page">
      <div className="tickets-header">
        <h1>Tickets</h1>
        <div className="tickets-header-actions">
          <select value={epicFilter} onChange={(e) => setEpicFilter(e.target.value)}>
            <option value="all">All epics</option>
            <option value="none">No epic</option>
            {epics?.map((epic) => (
              <option key={epic.id} value={epic.id}>
                {epic.title}
              </option>
            ))}
          </select>
          <button type="button" className="btn-primary" onClick={() => setShowNewForm((v) => !v)}>
            + New ticket
          </button>
        </div>
      </div>

      {error && <p role="alert">{error}</p>}

      {showNewForm && (
        <form className="ticket-new-form" onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Ticket title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            autoFocus
            required
          />
          <textarea
            placeholder="Acceptance criteria (required) — concrete, checkable statements of done"
            value={newAcceptanceCriteria}
            onChange={(e) => setNewAcceptanceCriteria(e.target.value)}
            rows={3}
            required
          />
          <select value={newPriority} onChange={(e) => setNewPriority(e.target.value as TicketPriority)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
          <select value={newEpicId} onChange={(e) => setNewEpicId(e.target.value)}>
            <option value="">No epic</option>
            {epics?.map((epic) => (
              <option key={epic.id} value={epic.id}>
                {epic.title}
              </option>
            ))}
          </select>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Adding..." : "Add"}
          </button>
        </form>
      )}

      {tickets === null && !error && <p>Loading...</p>}

      {tickets !== null && (
        <div className="ticket-board">
          {COLUMNS.map((column) => (
            <div
              key={column.status}
              className="ticket-column"
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => {
                if (draggedId !== null) moveTicket(draggedId, column.status);
                setDraggedId(null);
              }}
            >
              <div className="ticket-column-header">
                <span>{column.label}</span>
                <span className="ticket-column-count">
                  {visibleTickets.filter((t) => t.status === column.status).length}
                </span>
              </div>
              <div className="ticket-column-body">
                {visibleTickets
                  .filter((t) => t.status === column.status)
                  .map((ticket) => (
                    <TicketCard key={ticket.id} ticket={ticket} onDragStart={(_e, t) => setDraggedId(t.id)} />
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
