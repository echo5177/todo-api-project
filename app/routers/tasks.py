from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.enums import PriorityLevel
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("")
def list_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    done: Optional[bool] = Query(default=None),
    priority: Optional[PriorityLevel] = Query(default=None),
    due_before: Optional[date] = Query(default=None),
):
    statement = select(Task)

    if done is not None:
        statement = statement.where(Task.done == done)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    if due_before is not None:
        statement = statement.where(Task.due_date <= due_before)

    statement = statement.offset(offset).limit(limit)
    tasks = session.exec(statement).all()
    return tasks


@router.get("/{task_id}")
def get_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("")
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.done is not None:
        task.done = task_update.done
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
