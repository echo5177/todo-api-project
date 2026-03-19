from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel

from app.enums import PriorityLevel


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    done: bool = False
    priority: PriorityLevel = Field(default=PriorityLevel.medium)
    due_date: Optional[date] = None
