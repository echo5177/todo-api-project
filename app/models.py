from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from app.enums import PriorityLevel


def utcnow() -> datetime:
    """Timezone-aware current time, used as the default for timestamp fields."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    done: bool = False
    priority: PriorityLevel = Field(default=PriorityLevel.medium)
    due_date: Optional[date] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
