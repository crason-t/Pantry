from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

TICKET_STATUSES = ("backlog", "todo", "in_progress", "in_review", "done")
TICKET_PRIORITIES = ("low", "medium", "high", "urgent")

# This tracker is a single-user local dev tool -- no auth, no User table.
# Attribution fields are plain strings defaulting to the one person using it.
DEFAULT_USER = "carson"


class Epic(Base):
    __tablename__ = "epics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="#aa3bff")
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Nullable at the DB level only because it's assigned right after the initial
    # insert flush (needs the auto-generated id) -- always set by the time a
    # ticket is readable via the API.
    key: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Nullable at the DB level for pre-existing rows; required at the API layer
    # on creation -- every ticket must define what "done" means.
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="backlog")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    position: Mapped[float] = mapped_column(Float, default=0)
    labels: Mapped[list[str]] = mapped_column(JSONB, default=list)
    epic_id: Mapped[int | None] = mapped_column(ForeignKey("epics.id"), nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reporter: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    comments: Mapped[list["TicketComment"]] = relationship(
        back_populates="ticket", order_by="TicketComment.created_at", cascade="all, delete-orphan"
    )
    activity: Mapped[list["TicketActivity"]] = relationship(
        back_populates="ticket", order_by="TicketActivity.created_at", cascade="all, delete-orphan"
    )


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    author: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="comments")


class TicketActivity(Base):
    """Auto-logged field changes (status/priority/assignee/epic) for a ticket's history feed."""

    __tablename__ = "ticket_activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    actor: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    field: Mapped[str] = mapped_column(String(50))
    old_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="activity")
