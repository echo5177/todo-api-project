from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

sqlite_url = "sqlite:///test_database.db"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

SQLModel.metadata.create_all(engine)

client = TestClient(app)


def setup_function():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_create_task():
    response = client.post(
        "/tasks", json={"title": "Test task", "description": "Testing create"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Testing create"
    assert data["done"] is False
    assert "id" in data


def test_list_tasks():
    client.post("/tasks", json={"title": "Task 1", "description": "A"})
    client.post("/tasks", json={"title": "Task 2", "description": "B"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_task():
    create_response = client.post(
        "/tasks", json={"title": "Read book", "description": "Chapter 1"}
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read book"


def test_update_task_done():
    create_response = client.post(
        "/tasks", json={"title": "Finish homework", "description": "Math"}
    )
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True


def test_delete_task():
    create_response = client.post(
        "/tasks", json={"title": "Delete me", "description": "Temporary"}
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
