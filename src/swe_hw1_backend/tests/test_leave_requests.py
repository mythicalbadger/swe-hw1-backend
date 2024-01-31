"""Test the leave request endpoints."""
import datetime

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.swe_hw1_backend.models.leave_requests import LeaveRequest
from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.tests.conftest import ApiEndpoint
from src.swe_hw1_backend.utils.time_calc import date_from_iso_format

fake = Faker()


def test_create_leave_request(
    session: Session,
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request can be created."""
    response = client.post(
        url=ApiEndpoint.create_leave_request.value,
        json={
            "start_date": str(leave_request_fixture.start_date),
            "end_date": str(leave_request_fixture.end_date),
            "reason": leave_request_fixture.reason,
        },
        headers={"Authorization": f"Bearer {user_fixture.username}"},
    )
    data = response.json()
    response_start_date = date_from_iso_format(data["start_date"])
    response_end_date = date_from_iso_format(data["end_date"])

    assert response.status_code == status.HTTP_201_CREATED
    assert response_start_date == leave_request_fixture.start_date
    assert response_end_date == leave_request_fixture.end_date
    assert data["status"] == leave_request_fixture.status.value
    assert data["requester_id"] == user_fixture.id
    assert data["reason"] == leave_request_fixture.reason


def test_get_all_leave_requests(
    session: Session,
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that all leave requests can be fetched."""
    response = client.get(
        url=ApiEndpoint.get_all_leave_requests.value,
        headers={"Authorization": f"Bearer {user_fixture.username}"},
    )

    data = response.json()

    assert len(data) == 1

    print(data)

    fetched_leave_request = data[0]

    assert response.status_code == status.HTTP_200_OK
    assert fetched_leave_request["id"] == leave_request_fixture.id
    assert fetched_leave_request["requester_id"] == leave_request_fixture.requester_id
    assert (
        datetime.datetime.fromisoformat(fetched_leave_request["start_date"])
        == leave_request_fixture.start_date
    )
    assert (
        datetime.datetime.fromisoformat(fetched_leave_request["end_date"])
        == leave_request_fixture.end_date
    )
    assert fetched_leave_request["reason"] == leave_request_fixture.reason
    assert fetched_leave_request["status"] == "pending"


def test_delete_leave_request(
    session: Session,
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request can be deleted."""
    url = f"{ApiEndpoint.delete_leave_request.value}/{leave_request_fixture.id}"

    response = client.delete(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    leave_requests = session.exec(select(LeaveRequest)).all()

    assert response.status_code == status.HTTP_200_OK
    assert len(leave_requests) == 0


def test_approve_leave_request(
    session: Session,
    client: TestClient,
    admin_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request can be approved."""
    url = f"{ApiEndpoint.approve_leave_request.value}/{leave_request_fixture.id}"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {admin_fixture.username}"}
    )
    fetched_leave_request = session.get(LeaveRequest, leave_request_fixture.id)

    assert response.status_code == status.HTTP_200_OK
    assert fetched_leave_request.status == "approved"


def test_deny_leave_request(
    session: Session,
    client: TestClient,
    admin_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request can be denied."""
    url = f"{ApiEndpoint.deny_leave_request.value}/{leave_request_fixture.id}"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {admin_fixture.username}"}
    )
    fetched_leave_request = session.get(LeaveRequest, leave_request_fixture.id)

    assert response.status_code == status.HTTP_200_OK
    assert fetched_leave_request.status == "denied"


def test_deny_leave_request_if_not_admin(
    session: Session, client: TestClient, user_fixture: User
) -> None:
    """Test that a leave request cannot be denied if user is not admin."""
    url = f"{ApiEndpoint.deny_leave_request.value}/1"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_approve_leave_request_if_not_admin(
    session: Session, client: TestClient, user_fixture: User
) -> None:
    """Test that a leave request cannot be approved if user is not admin."""
    url = f"{ApiEndpoint.approve_leave_request.value}/1"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
