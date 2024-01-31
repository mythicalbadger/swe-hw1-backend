"""Test the user endpoints."""
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient

from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.utils import hasher
from swe_hw1_backend.tests.conftest import ApiEndpoint

fake = Faker()


def test_create_user(client: TestClient) -> None:
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
    assert data["remaining_leave_days"] == 10


def test_create_user_with_invalid_username(
    client: TestClient, user_fixture: User
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


def test_login_user(client: TestClient, user_fixture: User) -> None:
    """Test that a user can log in."""
    response = client.post(
        url=ApiEndpoint.login.value,
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


def test_login_user_with_invalid_credentials(
    client: TestClient, user_fixture: User
) -> None:
    """Test that a user cannot log in with invalid credentials."""
    response = client.post(
        url=ApiEndpoint.login.value,
        data={
            "username": user_fixture.username,
            "password": "wrong_password",
            "grant_type": "password",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"] == "Incorrect username or password."


def test_get_current_user(client: TestClient, user_fixture: User) -> None:
    """Test that the current user can be fetched."""
    response = client.get(
        url=ApiEndpoint.get_current_user.value,
        headers={"Authorization": f"Bearer {user_fixture.username}"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == user_fixture.id
    assert data["full_name"] == user_fixture.full_name
    assert data["username"] == user_fixture.username
    assert data["remaining_leave_days"] == user_fixture.remaining_leave_days
    assert data["is_admin"] == user_fixture.is_admin
