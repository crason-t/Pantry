from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.ticket import DEFAULT_USER, Epic, Ticket
from app.schemas.ticket import EpicCreate, EpicProgress, EpicRead

router = APIRouter(prefix="/epics", tags=["epics"])


@router.get("", response_model=list[EpicProgress])
def list_epics(db: Session = Depends(get_db)) -> list[dict]:
    epics = db.query(Epic).order_by(Epic.created_at).all()
    counts = dict(
        db.query(Ticket.epic_id, func.count(Ticket.id)).group_by(Ticket.epic_id).all()
    )
    done_counts = dict(
        db.query(Ticket.epic_id, func.count(Ticket.id))
        .filter(Ticket.status == "done")
        .group_by(Ticket.epic_id)
        .all()
    )
    return [
        {
            "id": epic.id,
            "title": epic.title,
            "description": epic.description,
            "color": epic.color,
            "created_at": epic.created_at,
            "ticket_count": counts.get(epic.id, 0),
            "done_count": done_counts.get(epic.id, 0),
        }
        for epic in epics
    ]


@router.post("", response_model=EpicRead, status_code=status.HTTP_201_CREATED)
def create_epic(payload: EpicCreate, db: Session = Depends(get_db)) -> Epic:
    epic = Epic(
        title=payload.title,
        description=payload.description,
        color=payload.color,
        created_by=DEFAULT_USER,
    )
    db.add(epic)
    db.commit()
    db.refresh(epic)
    return epic


@router.delete("/{epic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_epic(epic_id: int, db: Session = Depends(get_db)) -> None:
    epic = db.get(Epic, epic_id)
    if epic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Epic not found")
    db.query(Ticket).filter(Ticket.epic_id == epic_id).update({Ticket.epic_id: None})
    db.delete(epic)
    db.commit()
