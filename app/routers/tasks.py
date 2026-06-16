from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.enums import PriorityLevel
from app.models import Task, User, utcnow
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_user_task_or_404(session: Session, current_user: User, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
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

    # Deterministic, useful order: unfinished first, then by soonest due date
    # (undated tasks last), and finally newest first as a stable tie-breaker.
    statement = statement.order_by(
        Task.done,
        Task.due_date.is_(None),
        Task.due_date,
        Task.created_at.desc(),
    )

    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: SessionDep, current_user: CurrentUserDep):
    return get_user_task_or_404(session, current_user, task_id)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, session: SessionDep, current_user: CurrentUserDep):
    db_task = Task.model_validate(task)
    db_task.owner_id = current_user.id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    task = get_user_task_or_404(session, current_user, task_id)

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    if update_data:
        task.updated_at = utcnow()

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
