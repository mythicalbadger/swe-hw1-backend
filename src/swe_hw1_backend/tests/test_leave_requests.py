"""Test the leave request endpoints."""
import datetime
import typing

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app
from src.swe_hw1_backend.models.leave_requests import LeaveRequest
from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.utils import hasher

fake = Faker()
username = fake.user_name()
password = fake.password()
full_name = fake.name()
start_date = datetime.datetime.today()
end_date = start_date + datetime.timedelta(days=1)
reason = "I want to go to the moon."  # from copilot... it has dreams


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


def test_create_leave_request(session: Session, client: TestClient) -> None:
    """Test that a leave request can be created."""
    url = "/api/create-leave-request"

    user = User(
        username=username,
        full_name=full_name,
        hashed_password=hasher.hash(password),
    )
    session.add(user)
    session.commit()

    response = client.post(
        url=url,
        json={
            "start_date": str(start_date),
            "end_date": str(end_date),
            "reason": reason,
        },
        headers={"Authorization": f"Bearer {user.username}"}

    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert datetime.datetime.fromisoformat(data["start_date"]) == start_date
    assert datetime.datetime.fromisoformat(data["end_date"]) == end_date
    assert data["status"] == "pending"
    assert data["requester_id"] == user.id
    assert data["reason"] == reason


def test_get_all_leave_requests(session: Session, client: TestClient) -> None:
    """Test that all leave requests can be fetched."""
    url = "/api/get-all-leave-requests"

    user = User(
        username=username,
        full_name=full_name,
        hashed_password=hasher.hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    leave_request = LeaveRequest(
        requester_id=user.id,
        requester=user,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )

    session.add(leave_request)
    session.commit()

    response = client.get(
        url=url,
        headers={"Authorization": f"Bearer {user.username}"}
    )

    data = response.json()
    fetched_leave_request = data[0]

    assert response.status_code == status.HTTP_200_OK
    assert fetched_leave_request["id"] == leave_request.id
    assert fetched_leave_request["requester_id"] == user.id
    assert datetime.datetime.fromisoformat(fetched_leave_request["start_date"]) == start_date
    assert datetime.datetime.fromisoformat(fetched_leave_request["end_date"]) == end_date
    assert fetched_leave_request["reason"] == reason
    assert fetched_leave_request["status"] == "pending"


def test_delete_leave_request(session: Session, client: TestClient) -> None:
    """Test that a leave request can be deleted."""
    url = "/api/delete-leave-request/1"

    user = User(
        username=username,
        full_name=full_name,
        hashed_password=hasher.hash(password),
    )

    session.add(user)
    session.commit()

    session.refresh(user)

    leave_request = LeaveRequest(
        requester_id=user.id,
        requester=user,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )

    session.add(leave_request)
    session.add(user)
    session.commit()

    response = client.delete(
        url=url,
        headers={"Authorization": f"Bearer {user.username}"}
    )
    assert response.status_code == status.HTTP_200_OK

    leave_requests = session.exec(select(LeaveRequest)).all()
    assert len(leave_requests) == 0