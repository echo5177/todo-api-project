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
client = TestClient(app)


def setup_function():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def register_user(email: str, username: str, password: str):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )


def login_user(username: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_task():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Testing create",
            "priority": "high",
            "due_date": "2026-03-30",
        },
        headers=auth_headers(token),
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
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "A",
            "priority": "low",
            "due_date": "2026-03-28",
        },
        headers=auth_headers(token),
    )
    client.post(
        "/tasks",
        json={
            "title": "Task 2",
            "description": "B",
            "priority": "high",
            "due_date": "2026-03-20",
        },
        headers=auth_headers(token),
    )

    response = client.get("/tasks", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_task():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={
            "title": "Read book",
            "description": "Chapter 1",
            "priority": "medium",
            "due_date": "2026-03-26",
        },
        headers=auth_headers(token),
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read book"
    assert data["priority"] == "medium"


def test_update_task_done_and_priority():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={
            "title": "Finish homework",
            "description": "Math",
            "priority": "low",
            "due_date": "2026-03-29",
        },
        headers=auth_headers(token),
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"done": True, "priority": "high"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True
    assert data["priority"] == "high"


def test_delete_task():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete me",
            "description": "Temporary",
            "priority": "medium",
            "due_date": "2026-03-31",
        },
        headers=auth_headers(token),
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
    )
    assert delete_response.status_code == 200

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
    )
    assert get_response.status_code == 404


def test_filter_by_priority():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    client.post(
        "/tasks",
        json={
            "title": "Low task",
            "description": "Easy",
            "priority": "low",
            "due_date": "2026-03-28",
        },
        headers=auth_headers(token),
    )
    client.post(
        "/tasks",
        json={
            "title": "High task",
            "description": "Urgent",
            "priority": "high",
            "due_date": "2026-03-20",
        },
        headers=auth_headers(token),
    )

    response = client.get("/tasks?priority=high", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High task"
    assert data[0]["priority"] == "high"


def test_invalid_priority_should_fail():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    response = client.post(
        "/tasks",
        json={
            "title": "Bad priority",
            "description": "Wrong value",
            "priority": "urgent",
            "due_date": "2026-03-28",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422


def test_invalid_due_date_should_fail():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    response = client.post(
        "/tasks",
        json={
            "title": "Bad date",
            "description": "Wrong date format",
            "priority": "medium",
            "due_date": "2026/03/28",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422


def test_user_can_only_see_own_tasks():
    register_user("alice@example.com", "alice", "secret123")
    register_user("bob@example.com", "bob", "secret456")

    alice_token = login_user("alice", "secret123")
    bob_token = login_user("bob", "secret456")

    create_response = client.post(
        "/tasks",
        json={
            "title": "Alice private task",
            "description": "Only alice should see this",
            "priority": "high",
            "due_date": "2026-03-30",
        },
        headers=auth_headers(alice_token),
    )
    alice_task_id = create_response.json()["id"]

    alice_list = client.get("/tasks", headers=auth_headers(alice_token))
    assert alice_list.status_code == 200
    assert len(alice_list.json()) == 1

    bob_list = client.get("/tasks", headers=auth_headers(bob_token))
    assert bob_list.status_code == 200
    assert len(bob_list.json()) == 0

    bob_get_alice_task = client.get(
        f"/tasks/{alice_task_id}",
        headers=auth_headers(bob_token),
    )
    assert bob_get_alice_task.status_code == 404


def test_unauthenticated_user_cannot_access_tasks():
    response = client.get("/tasks")
    assert response.status_code == 401
