from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlmodel import Field, Session, SQLModel, create_engine, select


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="My Todo API", lifespan=lifespan)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    done: bool = False


class TaskCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=50)
    description: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    done: Optional[bool] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def read_root():
    return {"message": "Todo API is running"}


@app.get("/tasks")
def list_tasks(session: SessionDep, done: Optional[bool] = Query(default=None)):
    statement = select(Task)
    if done is not None:
        statement = statement.where(Task.done == done)
    tasks = session.exec(statement).all()
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks")
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task(title=task.title, description=task.description)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.patch("/tasks/{task_id}")
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

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
