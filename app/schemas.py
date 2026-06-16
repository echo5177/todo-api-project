from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.enums import PriorityLevel


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: str = ""
    priority: PriorityLevel = PriorityLevel.medium
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    done: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[date] = None


class TaskRead(BaseModel):
    """Public view of a task. Deliberately omits ``owner_id`` so the API never
    leaks internal ownership wiring to clients."""

    id: int
    title: str
    description: str
    done: bool
    priority: PriorityLevel
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6, max_length=100)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
