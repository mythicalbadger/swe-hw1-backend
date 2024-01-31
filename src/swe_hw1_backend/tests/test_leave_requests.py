"""Test the leave request endpoints."""
import datetime

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response
from sqlmodel import Session, select

from src.swe_hw1_backend.models.leave_requests import LeaveRequest
from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.tests.conftest import ApiEndpoint
from src.swe_hw1_backend.utils.time_calc import date_from_iso_format

fake = Faker()


def send_one_day_leave_request(
    client: TestClient, start_date: datetime.datetime, reason: str, username: str
) -> Response:
    """Send a leave request for one day."""
    end_date = start_date + datetime.timedelta(days=1)

    response = client.post(
        url=ApiEndpoint.create_leave_request.value,
        json={
            "start_date": str(start_date),
            "end_date": str(end_date),
            "reason": reason,
        },
        headers={"Authorization": f"Bearer {username}"},
    )

    return response


def test_create_leave_request(
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request can be created."""
    start_date = leave_request_fixture.start_date + datetime.timedelta(days=69)
    response = send_one_day_leave_request(
        client, start_date, leave_request_fixture.reason, user_fixture.username
    )
    data = response.json()

    response_start_date = date_from_iso_format(data["start_date"])
    response_end_date = date_from_iso_format(data["end_date"])

    assert response.status_code == status.HTTP_201_CREATED
    assert response_start_date == start_date
    assert response_end_date == start_date + datetime.timedelta(days=1)
    assert data["status"] == leave_request_fixture.status.value
    assert data["requester_id"] == user_fixture.id
    assert data["reason"] == leave_request_fixture.reason
    assert user_fixture.remaining_leave_days == 8


def test_create_leave_request_if_not_enough_leave_days(
    session: Session,
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request cannot be created if not enough leave days."""
    user_fixture.remaining_leave_days = 0
    session.add(user_fixture)
    session.commit()

    start_date = leave_request_fixture.start_date + datetime.timedelta(days=69)
    response = send_one_day_leave_request(
        client, start_date, leave_request_fixture.reason, user_fixture.username
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Not enough remaining leave days."


def test_create_leave_request_if_date_not_two_months_in_advance(
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a leave request cannot be created if not two months in advance."""
    start_date = datetime.datetime.today()

    response = send_one_day_leave_request(
        client, start_date, leave_request_fixture.reason, user_fixture.username
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        data["detail"] == "Leave request must be made at least two months in advance."
    )


def test_user_cannot_create_overlapping_leave_request(
    client: TestClient,
    user_fixture: User,
    leave_request_fixture: LeaveRequest,
) -> None:
    """Test that a user cannot create an overlapping leave request."""
    start_date = leave_request_fixture.start_date
    response = send_one_day_leave_request(
        client, start_date, leave_request_fixture.reason, user_fixture.username
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Leave request overlaps with another leave request."


def test_get_all_leave_requests(
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


def test_delete_leave_request_if_date_passed(
    session: Session,
    client: TestClient,
    user_fixture: User,
):
    """Test that a leave request cannot be deleted if the leave has started."""
    start_date = datetime.datetime.today() - datetime.timedelta(days=1)
    end_date = datetime.datetime.today()
    reason = "I want to go to the moon."
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

    url = f"{ApiEndpoint.delete_leave_request.value}/{leave_request.id}"

    response = client.delete(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    leave_requests = session.exec(select(LeaveRequest)).all()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "Cannot delete leave request after leave has started."
    )
    assert len(leave_requests) == 1


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
    client: TestClient, user_fixture: User
) -> None:
    """Test that a leave request cannot be denied if user is not admin."""
    url = f"{ApiEndpoint.deny_leave_request.value}/1"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_approve_leave_request_if_not_admin(
    client: TestClient, user_fixture: User
) -> None:
    """Test that a leave request cannot be approved if user is not admin."""
    url = f"{ApiEndpoint.approve_leave_request.value}/1"
    response = client.put(
        url=url, headers={"Authorization": f"Bearer {user_fixture.username}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
