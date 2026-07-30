from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.models.ticket import DEFAULT_USER, Ticket, TicketActivity, TicketComment
from app.schemas.ticket import CommentCreate, CommentRead, TicketCreate, TicketRead, TicketSummary, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Fields that get an activity-log entry when changed via PATCH.
TRACKED_FIELDS = ("status", "priority", "assignee", "epic_id", "test_url")

# TicketActivity.old_value/new_value are String(255); test_url can be up to 1000.
ACTIVITY_VALUE_MAX = 255


def _activity_value(value: object) -> str | None:
    return str(value)[:ACTIVITY_VALUE_MAX] if value is not None else None


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
    assignee: str | None = None,
    db: Session = Depends(get_db),
) -> list[Ticket]:
    query = db.query(Ticket)
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if epic_id is not None:
        query = query.filter(Ticket.epic_id == epic_id)
    if assignee is not None:
        query = query.filter(Ticket.assignee == assignee)
    return query.order_by(Ticket.status, Ticket.position).all()


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    max_position = (
        db.query(Ticket.position).filter(Ticket.status == payload.status).order_by(Ticket.position.desc()).first()
    )
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        acceptance_criteria=payload.acceptance_criteria,
        test_url=payload.test_url,
        status=payload.status,
        priority=payload.priority,
        labels=payload.labels,
        epic_id=payload.epic_id,
        assignee=payload.assignee,
        reporter=DEFAULT_USER,
        position=(max_position[0] + 1) if max_position else 0,
    )
    db.add(ticket)
    db.flush()
    ticket.key = f"PANTRY-{ticket.id}"
    db.commit()
    db.refresh(ticket)
    return _get_ticket_or_404(db, ticket.id)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    return _get_ticket_or_404(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)) -> Ticket:
    ticket = _get_ticket_or_404(db, ticket_id)
    changes = payload.model_dump(exclude_unset=True)

    for field in TRACKED_FIELDS:
        if field in changes and changes[field] != getattr(ticket, field):
            db.add(
                TicketActivity(
                    ticket_id=ticket.id,
                    actor=DEFAULT_USER,
                    field=field,
                    old_value=_activity_value(getattr(ticket, field)),
                    new_value=_activity_value(changes[field]),
                )
            )

    for field, value in changes.items():
        setattr(ticket, field, value)

    db.commit()
    return _get_ticket_or_404(db, ticket_id)  # reload with fresh activity


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)) -> None:
    ticket = _get_ticket_or_404(db, ticket_id)
    db.delete(ticket)
    db.commit()


@router.post("/{ticket_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(ticket_id: int, payload: CommentCreate, db: Session = Depends(get_db)) -> TicketComment:
    _get_ticket_or_404(db, ticket_id)  # 404s if the ticket doesn't exist
    comment = TicketComment(ticket_id=ticket_id, author=DEFAULT_USER, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
