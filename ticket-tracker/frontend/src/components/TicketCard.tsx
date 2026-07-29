import { Link } from "react-router-dom";
import type { TicketSummary } from "../api/types";

const PRIORITY_LABEL: Record<TicketSummary["priority"], string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

export function TicketCard({
  ticket,
  onDragStart,
}: {
  ticket: TicketSummary;
  onDragStart: (event: React.DragEvent, ticket: TicketSummary) => void;
}) {
  return (
    <Link
      to={`/tickets/${ticket.id}`}
      className="ticket-card"
      draggable
      onDragStart={(event) => onDragStart(event, ticket)}
    >
      <div className="ticket-card-top">
        <span className="ticket-key">{ticket.key}</span>
        <span className="ticket-priority" data-priority={ticket.priority}>
          {PRIORITY_LABEL[ticket.priority]}
        </span>
      </div>
      <p className="ticket-card-title">{ticket.title}</p>
      {ticket.labels.length > 0 && (
        <div className="ticket-card-labels">
          {ticket.labels.map((label) => (
            <span key={label} className="ticket-label">
              {label}
            </span>
          ))}
        </div>
      )}
      {ticket.assignee && <span className="ticket-assignee">{ticket.assignee}</span>}
    </Link>
  );
}
