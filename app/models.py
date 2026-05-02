from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel

from app.enums import PriorityLevel


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
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
