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
        "/tasks",
        json={
            "title": "Test task",
            "description": "Testing create",
            "priority": "high",
            "due_date": "2026-03-30",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Testing create"
    assert data["done"] is False
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-03-30"
    assert "id" in data


def test_list_tasks():
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "A",
            "priority": "low",
            "due_date": "2026-03-28",
        },
    )
    client.post(
        "/tasks",
        json={
            "title": "Task 2",
            "description": "B",
            "priority": "high",
            "due_date": "2026-03-20",
        },
    )

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Read book",
            "description": "Chapter 1",
            "priority": "medium",
            "due_date": "2026-03-26",
        },
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read book"
    assert data["priority"] == "medium"


def test_update_task_done_and_priority():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Finish homework",
            "description": "Math",
            "priority": "low",
            "due_date": "2026-03-29",
        },
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"done": True, "priority": "high"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True
    assert data["priority"] == "high"


def test_delete_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete me",
            "description": "Temporary",
            "priority": "medium",
            "due_date": "2026-03-31",
        },
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_filter_by_priority():
    client.post(
        "/tasks",
        json={
            "title": "Low task",
            "description": "Easy",
            "priority": "low",
            "due_date": "2026-03-28",
        },
    )
    client.post(
        "/tasks",
        json={
            "title": "High task",
            "description": "Urgent",
            "priority": "high",
            "due_date": "2026-03-20",
        },
    )

    response = client.get("/tasks?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High task"
    assert data[0]["priority"] == "high"


def test_invalid_priority_should_fail():
    response = client.post(
        "/tasks",
        json={
            "title": "Bad priority",
            "description": "Wrong value",
            "priority": "urgent",
            "due_date": "2026-03-28",
        },
    )
    assert response.status_code == 422


def test_invalid_due_date_should_fail():
    response = client.post(
        "/tasks",
        json={
            "title": "Bad date",
            "description": "Wrong date format",
            "priority": "medium",
            "due_date": "2026/03/28",
        },
    )
    assert response.status_code == 422


def test_delete_task_not_found():
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_cors_headers():
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Custom-Header",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:8000"
    )
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_filter_by_due_before():
    client.post(
        "/tasks",
        json={
            "title": "Early task",
            "description": "Due early",
            "priority": "medium",
            "due_date": "2026-03-20",
        },
    )
    client.post(
        "/tasks",
        json={
            "title": "Late task",
            "description": "Due late",
            "priority": "medium",
            "due_date": "2026-03-30",
        },
    )

    response = client.get("/tasks?due_before=2026-03-25")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Early task"
    assert data[0]["due_date"] == "2026-03-20"
