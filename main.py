from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="My Todo API")

tasks = []
next_id = 1


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    done: bool | None = None


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


@app.get("/")
def read_root():
    return {"message": "Todo API is running"}


@app.get("/tasks")
def list_tasks(done: bool | None = None):
    if done is None:
        return tasks
    return [task for task in tasks if task["done"] == done]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks")
def create_task(task: TaskCreate):
    global next_id

    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "done": False
    }
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        task["title"] = task_update.title
    if task_update.description is not None:
        task["description"] = task_update.description
    if task_update.done is not None:
        task["done"] = task_update.done

    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks.remove(task)
    return {"message": "Task deleted successfully"}









# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI(title="My Todo API")

# tasks = []

# class TaskCreate(BaseModel):
#     title: str
    
# @app.get("/")
# def read_root():
#     return {"message": "Todo API is running"}


# @app.get("/tasks")
# def list_tasks():
#     return tasks


# @app.post("/tasks")
# def create_task(task: TaskCreate):
#     new_task = {
#         "id": len(tasks) + 1,
#         "title": task.title,
#         "done": False
#     }
#     tasks.append(new_task)
#     return new_task
