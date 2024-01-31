"""Test the user endpoints."""
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.utils import hasher
from swe_hw1_backend.tests.conftest import ApiEndpoint

fake = Faker()


def test_create_user(session: Session, client: TestClient) -> None:
    """Test that a user can be created."""
    username = fake.user_name()
    password = fake.password()
    full_name = fake.name()

    response = client.post(
        url=ApiEndpoint.register.value,
        json={"username": username, "password": password, "full_name": full_name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["full_name"] == full_name
    assert data["username"] == username
    assert hasher.verify(password, bytes(data["hashed_password"], "utf-8")) is True
    assert data["remaining_leave_days"] == 42


def test_create_user_with_invalid_username(
    session: Session, client: TestClient, user_fixture: User
) -> None:
    """Test that a user cannot be created with an invalid username."""
    response = client.post(
        url=ApiEndpoint.register.value,
        json={
            "username": user_fixture.username,
            "password": user_fixture.username,
            "full_name": user_fixture.full_name,
        },
    )
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Username already taken."


def test_login_user(session: Session, client: TestClient, user_fixture: User) -> None:
    """Test that a user can log in."""
    response = client.post(
        "/token",
        data={
            "username": user_fixture.username,
            "password": "password",
            "grant_type": "password",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["token_type"] == "bearer"
    assert data["access_token"] == user_fixture.username
