from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.database import get_session
from app.main import app
from app.models import User

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


def test_register_user_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == "alice@example.com")
        ).first()
        assert user is not None
        assert user.hashed_password != "secret123"


def test_register_duplicate_email_should_fail():
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice2",
            "password": "secret456",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_duplicate_username_should_fail():
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "username": "alice",
            "password": "secret456",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_login_success_returns_token():
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/token",
        data={
            "username": "alice",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_should_fail():
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/token",
        data={
            "username": "alice",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user_with_valid_token():
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "secret123",
        },
    )

    login_response = client.post(
        "/auth/token",
        data={
            "username": "alice",
            "password": "secret123",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
