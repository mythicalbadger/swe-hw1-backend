import datetime
import enum
import typing

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from src.database import get_session
from src.main import app
from src.swe_hw1_backend.models.leave_requests import LeaveRequest
from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.utils import hasher

admin_username = "admin"
username = "username"
password = "password"
full_name = "fullname"


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


@pytest.fixture()
def user_fixture(session: Session) -> User:
    """Create a user."""
    user = User(
        username=username,
        full_name=full_name,
        hashed_password=hasher.hash(password),
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    yield user


@pytest.fixture()
def admin_fixture(session: Session) -> User:
    """Create an admin user."""
    user = User(
        username=admin_username,
        full_name=full_name,
        hashed_password=hasher.hash(password),
        is_admin=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    yield user


@pytest.fixture()
def leave_request_fixture(session: Session, user_fixture: User) -> LeaveRequest:
    """Create a leave request."""
    start_date = datetime.datetime.today() + datetime.timedelta(days=69)
    end_date = start_date + datetime.timedelta(days=1)
    reason = "I want to go to the moon."  # from copilot... it has dreams
    leave_request = LeaveRequest(
        requester_id=user_fixture.id,
        requester=user_fixture,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )
    session.add(leave_request)
    session.commit()
    session.refresh(leave_request)

    yield leave_request


class ApiEndpoint(enum.Enum):
    """Enum for API endpoints."""

    get_current_user = "/api/get-current-user"
    register = "/register"
    login = "/token"
    create_leave_request = "/api/create-leave-request"
    get_all_leave_requests = "/api/get-all-leave-requests"
    delete_leave_request = "/api/delete-leave-request"
    approve_leave_request = "/api/approve-leave-request"
    deny_leave_request = "/api/deny-leave-request"
