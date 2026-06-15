from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

sqlite_url = "sqlite://"
connect_args = {"check_same_thread": False}
engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    poolclass=StaticPool,
)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def setup_function():
    app.dependency_overrides[get_session] = override_get_session
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

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Testing create"
    assert data["done"] is False
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-03-30"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # The public task schema must never leak internal ownership wiring.
    assert "owner_id" not in data


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


def test_filter_by_due_before():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    client.post(
        "/tasks",
        json={
            "title": "Early task",
            "description": "Due early",
            "priority": "medium",
            "due_date": "2026-03-20",
        },
        headers=auth_headers(token),
    )
    client.post(
        "/tasks",
        json={
            "title": "Late task",
            "description": "Due late",
            "priority": "medium",
            "due_date": "2026-03-30",
        },
        headers=auth_headers(token),
    )

    response = client.get(
        "/tasks?due_before=2026-03-25",
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Early task"
    assert data[0]["due_date"] == "2026-03-20"


def test_filter_by_title():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    client.post(
        "/tasks",
        json={
            "title": "Buy coffee",
            "description": "Beans",
            "priority": "low",
            "due_date": "2026-03-28",
        },
        headers=auth_headers(token),
    )
    client.post(
        "/tasks",
        json={
            "title": "Write report",
            "description": "Weekly update",
            "priority": "high",
            "due_date": "2026-03-30",
        },
        headers=auth_headers(token),
    )

    response = client.get("/tasks?title=coffee", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Buy coffee"


def test_list_tasks_pagination():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    for index in range(15):
        client.post(
            "/tasks",
            json={
                "title": f"Pagination Task {index}",
                "description": "Testing limits",
                "priority": "low",
                "due_date": "2026-03-28",
            },
            headers=auth_headers(token),
        )

    response = client.get("/tasks?limit=5", headers=auth_headers(token))
    assert response.status_code == 200
    first_page = response.json()
    assert len(first_page) == 5

    response = client.get("/tasks?limit=5&offset=5", headers=auth_headers(token))
    assert response.status_code == 200
    second_page = response.json()
    assert len(second_page) == 5
    assert first_page[0]["id"] != second_page[0]["id"]


def test_list_tasks_limit_exceeded():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    response = client.get("/tasks?limit=101", headers=auth_headers(token))
    assert response.status_code == 422


def test_patch_task_can_clear_due_date():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={
            "title": "Task with date",
            "description": "Clear the date later",
            "priority": "medium",
            "due_date": "2026-03-28",
        },
        headers=auth_headers(token),
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"due_date": None},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["due_date"] is None


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


def test_list_orders_pending_by_due_date_then_undated_last():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    def create(title, due_date=None):
        client.post(
            "/tasks",
            json={"title": title, "due_date": due_date},
            headers=auth_headers(token),
        )

    create("No due date")
    create("Due late", "2026-04-10")
    create("Due soon", "2026-04-01")

    response = client.get("/tasks", headers=auth_headers(token))
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Due soon", "Due late", "No due date"]


def test_completed_tasks_sort_after_pending():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Will be done"},
        headers=auth_headers(token),
    )
    done_id = create_response.json()["id"]
    client.post("/tasks", json={"title": "Still pending"}, headers=auth_headers(token))

    client.patch(
        f"/tasks/{done_id}",
        json={"done": True},
        headers=auth_headers(token),
    )

    response = client.get("/tasks", headers=auth_headers(token))
    titles = [task["title"] for task in response.json()]
    assert titles == ["Still pending", "Will be done"]


def test_update_bumps_updated_at_timestamp():
    register_user("alice@example.com", "alice", "secret123")
    token = login_user("alice", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Track timestamps"},
        headers=auth_headers(token),
    )
    created = create_response.json()

    update_response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Track timestamps (edited)"},
        headers=auth_headers(token),
    )
    updated = update_response.json()

    assert updated["created_at"] == created["created_at"]
    assert updated["updated_at"] >= created["updated_at"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
