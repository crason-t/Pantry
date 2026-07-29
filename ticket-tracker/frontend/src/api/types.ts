export type TicketStatus = "backlog" | "todo" | "in_progress" | "in_review" | "done";
export type TicketPriority = "low" | "medium" | "high" | "urgent";

export interface EpicProgress {
  id: number;
  title: string;
  description: string | null;
  color: string;
  created_at: string;
  ticket_count: number;
  done_count: number;
}

export interface CommentRead {
  id: number;
  body: string;
  created_at: string;
  author: string;
}

export interface ActivityRead {
  id: number;
  field: string;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
  actor: string;
}

export interface TicketSummary {
  id: number;
  key: string;
  title: string;
  status: TicketStatus;
  priority: TicketPriority;
  labels: string[];
  position: number;
  epic_id: number | null;
  assignee: string | null;
  updated_at: string;
}

export interface Ticket extends TicketSummary {
  description: string | null;
  reporter: string;
  created_at: string;
  comments: CommentRead[];
  activity: ActivityRead[];
}
