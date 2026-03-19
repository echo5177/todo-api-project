from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

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
