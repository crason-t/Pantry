from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.models.ticket import Ticket, TicketActivity, TicketComment
from app.models.user import User
from app.schemas.ticket import CommentCreate, CommentRead, TicketCreate, TicketRead, TicketSummary, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Fields that get an activity-log entry when changed via PATCH.
TRACKED_FIELDS = ("status", "priority", "assignee_id", "epic_id")


def _user_summary(user: User | None) -> dict | None:
    if user is None:
        return None
    return {"id": user.id, "username": user.username}


def _load_users(db: Session, user_ids: set[int]) -> dict[int, User]:
    user_ids.discard(None)
    if not user_ids:
        return {}
    return {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}


def _ticket_summary_dict(ticket: Ticket, users: dict[int, User]) -> dict:
    return {
        "id": ticket.id,
        "key": ticket.key,
        "title": ticket.title,
        "status": ticket.status,
        "priority": ticket.priority,
        "labels": ticket.labels,
        "position": ticket.position,
        "epic_id": ticket.epic_id,
        "assignee": _user_summary(users.get(ticket.assignee_id)),
        "updated_at": ticket.updated_at,
    }


def _ticket_read_dict(ticket: Ticket, db: Session) -> dict:
    user_ids = {ticket.assignee_id, ticket.reporter_id}
    user_ids.update(c.author_id for c in ticket.comments)
    user_ids.update(a.user_id for a in ticket.activity)
    users = _load_users(db, user_ids)

    return {
        **_ticket_summary_dict(ticket, users),
        "description": ticket.description,
        "reporter": _user_summary(users.get(ticket.reporter_id)),
        "created_at": ticket.created_at,
        "comments": [
            {
                "id": c.id,
                "body": c.body,
                "created_at": c.created_at,
                "author": _user_summary(users.get(c.author_id)),
            }
            for c in ticket.comments
        ],
        "activity": [
            {
                "id": a.id,
                "field": a.field,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "created_at": a.created_at,
                "user": _user_summary(users.get(a.user_id)),
            }
            for a in ticket.activity
        ],
    }


def _get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = (
        db.query(Ticket)
        .options(selectinload(Ticket.comments), selectinload(Ticket.activity))
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.get("", response_model=list[TicketSummary])
def list_tickets(
    status_filter: str | None = Query(default=None, alias="status"),
    epic_id: int | None = None,
    assignee_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(Ticket)
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if epic_id is not None:
        query = query.filter(Ticket.epic_id == epic_id)
    if assignee_id is not None:
        query = query.filter(Ticket.assignee_id == assignee_id)
    tickets = query.order_by(Ticket.status, Ticket.position).all()

    user_ids = {t.assignee_id for t in tickets}
    users = _load_users(db, user_ids)
    return [_ticket_summary_dict(t, users) for t in tickets]


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    max_position = (
        db.query(Ticket.position).filter(Ticket.status == payload.status).order_by(Ticket.position.desc()).first()
    )
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        labels=payload.labels,
        epic_id=payload.epic_id,
        assignee_id=payload.assignee_id,
        reporter_id=current_user.id,
        position=(max_position[0] + 1) if max_position else 0,
    )
    db.add(ticket)
    db.flush()
    ticket.key = f"PANTRY-{ticket.id}"
    db.commit()
    db.refresh(ticket)
    return _ticket_read_dict(ticket, db)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ticket = _get_ticket_or_404(db, ticket_id)
    return _ticket_read_dict(ticket, db)


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ticket = _get_ticket_or_404(db, ticket_id)
    changes = payload.model_dump(exclude_unset=True)

    for field in TRACKED_FIELDS:
        if field in changes and changes[field] != getattr(ticket, field):
            db.add(
                TicketActivity(
                    ticket_id=ticket.id,
                    user_id=current_user.id,
                    field=field,
                    old_value=str(getattr(ticket, field)) if getattr(ticket, field) is not None else None,
                    new_value=str(changes[field]) if changes[field] is not None else None,
                )
            )

    for field, value in changes.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    ticket = _get_ticket_or_404(db, ticket_id)  # reload with fresh activity
    return _ticket_read_dict(ticket, db)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    ticket = _get_ticket_or_404(db, ticket_id)
    db.delete(ticket)
    db.commit()


@router.post("/{ticket_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(
    ticket_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _get_ticket_or_404(db, ticket_id)  # 404s if the ticket doesn't exist
    comment = TicketComment(ticket_id=ticket_id, author_id=current_user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "body": comment.body,
        "created_at": comment.created_at,
        "author": _user_summary(current_user),
    }
