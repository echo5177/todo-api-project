from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.enums import PriorityLevel
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_user_task_or_404(session: Session, current_user: User, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("")
def list_tasks(
    session: SessionDep,
    current_user: CurrentUserDep,
    done: Optional[bool] = Query(default=None),
    priority: Optional[PriorityLevel] = Query(default=None),
    due_before: Optional[date] = Query(default=None),
    title: Optional[str] = Query(default=None),
):
    statement = select(Task).where(Task.owner_id == current_user.id)

    if done is not None:
        statement = statement.where(Task.done == done)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    if due_before is not None:
        statement = statement.where(Task.due_date <= due_before)

    if title is not None:
        statement = statement.where(Task.title.contains(title))

    tasks = session.exec(statement).all()
    return tasks


@router.get("/{task_id}")
def get_task(task_id: int, session: SessionDep, current_user: CurrentUserDep):
    task = get_user_task_or_404(session, current_user, task_id)
    return task


@router.post("")
def create_task(task: TaskCreate, session: SessionDep, current_user: CurrentUserDep):
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        owner_id=current_user.id,
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    task = get_user_task_or_404(session, current_user, task_id)

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
def delete_task(task_id: int, session: SessionDep, current_user: CurrentUserDep):
    task = get_user_task_or_404(session, current_user, task_id)

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
