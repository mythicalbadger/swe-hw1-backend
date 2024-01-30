"""Test the user endpoints."""
import typing

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app
from src.swe_hw1_backend.utils import hasher
from swe_hw1_backend.models.users import User

username = "test"
password = "password"
full_name = "test user"


@pytest.fixture(name="session")
def session_fixture() -> Session:
    """Create a new database session for each test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> typing.Generator:
    """Override the get_session dependency to use the session fixture."""

    def get_session_override() -> Session:
        """Return the session fixture."""
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_user(session: Session, client: TestClient) -> None:
    """Test that a user can be created."""
    url = "/register"

    response = client.post(
        url=url,
        json={"username": username, "password": password, "full_name": full_name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["full_name"] == full_name
    assert data["username"] == username
    assert hasher.verify(password, bytes(data["hashed_password"], "utf-8")) is True
    assert data["remaining_leave_days"] == 42


def test_create_user_with_invalid_username(
    session: Session, client: TestClient
) -> None:
    """Test that a user cannot be created with an invalid username."""
    url = "/register"

    client.post(
        url=url,
        json={"username": username, "password": password, "full_name": full_name},
    )

    response = client.post(
        url=url,
        json={"username": username, "password": password, "full_name": full_name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Username already taken."


def test_login_user(session: Session, client: TestClient) -> None:
    """Test that a user can log in."""
    user = User(
        full_name=full_name,
        username=username,
        hashed_password=hasher.hash(password),
        remaining_leave_days=42,
    )

    session.add(user)
    session.commit()

    response = client.post(
        "/token",
        data={"username": username, "password": password, "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["token_type"] == "bearer"
    assert data["access_token"] == username
