from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

TicketStatus = Literal["backlog", "todo", "in_progress", "in_review", "done"]
TicketPriority = Literal["low", "medium", "high", "urgent"]


class EpicCreate(BaseModel):
    title: str
    description: str | None = None
    color: str = "#aa3bff"


class EpicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    color: str
    created_at: datetime


class EpicProgress(EpicRead):
    ticket_count: int
    done_count: int


class TicketCreate(BaseModel):
    title: str
    description: str | None = None
    status: TicketStatus = "backlog"
    priority: TicketPriority = "medium"
    labels: list[str] = []
    epic_id: int | None = None
    assignee: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    labels: list[str] | None = None
    epic_id: int | None = None
    assignee: str | None = None
    position: float | None = None


class CommentCreate(BaseModel):
    body: str


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str
    created_at: datetime
    author: str


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    field: str
    old_value: str | None
    new_value: str | None
    created_at: datetime
    actor: str


class TicketSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    title: str
    status: TicketStatus
    priority: TicketPriority
    labels: list[str]
    position: float
    epic_id: int | None
    assignee: str | None
    updated_at: datetime


class TicketRead(TicketSummary):
    description: str | None
    reporter: str
    created_at: datetime
    comments: list[CommentRead]
    activity: list[ActivityRead]
