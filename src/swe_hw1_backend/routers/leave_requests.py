"""Leave requests router."""
import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from src.database import get_session
from src.swe_hw1_backend.models.leave_requests import LeaveRequest, LeaveRequestStatus
from src.swe_hw1_backend.models.users import User
from src.swe_hw1_backend.routers.users import get_current_user
from src.swe_hw1_backend.schemas.leave_requests import LeaveRequestCreate
from src.swe_hw1_backend.services.leave_requests import LeaveRequestService
from src.swe_hw1_backend.services.users import UserService
from src.swe_hw1_backend.utils.time_calc import days_between, is_two_months_in_advance

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post(
    "/api/create-leave-request",
    tags=["leave-requests"],
    response_model=LeaveRequest,
    status_code=status.HTTP_201_CREATED,
)
async def create_leave_request(
    leave_request_info: LeaveRequestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> LeaveRequest:
    """
    Create a leave request.

    :param leave_request_info: The leave request info object.
    :param current_user: Current user object.
    :param session: Database session.
    :return: A created leave request object.
    """
    leave_request: LeaveRequest = LeaveRequest(
        requester_id=current_user.id,
        requester=current_user,
        **leave_request_info.model_dump()
    )
    days_requested: int = days_between(leave_request.start_date, leave_request.end_date)

    print(days_requested)

    if not is_two_months_in_advance(leave_request.start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request must be made at least two months in advance.",
        )
    elif days_requested > current_user.remaining_leave_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough remaining leave days.",
        )
    elif LeaveRequestService(session).is_date_in_leave_requests(
        leave_request.start_date, current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request overlaps with another leave request.",
        )

    LeaveRequestService(session).create_leave_request(leave_request=leave_request)
    UserService(session).deduct_remaining_leave_days(
        username=current_user.username, days=days_requested
    )

    return LeaveRequestService(session).get_leave_request_by_id(leave_request.id)


@router.get("/api/get-all-leave-requests", tags=["leave-requests"])
async def get_all_leave_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> List[LeaveRequest]:
    """
    Get all leave requests.

    :param current_user: The current user.
    :param session: The database session.
    :return: a list of all leave requests.
    """
    leave_requests: List[LeaveRequest] = LeaveRequestService(
        session
    ).get_all_leave_requests()
    return leave_requests


@router.delete("/api/delete-leave-request/{leave_request_id}", tags=["leave-requests"])
async def delete_leave_request(
    leave_request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    """
    Delete a leave request.

    :param leave_request_id: The id of the leave request to delete.
    :param current_user: The current user.
    :param session: The database session.
    """
    leave_request: LeaveRequest = LeaveRequestService(session).get_leave_request_by_id(
        leave_request_id
    )

    if leave_request.start_date < datetime.datetime.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete leave request after leave has started.",
        )

    leave_days: int = days_between(leave_request.start_date, leave_request.end_date)
    UserService(session).increment_remaining_leave_days(
        current_user.username, leave_days
    )
    LeaveRequestService(session).delete_leave_request(leave_request_id)


@router.put("/api/approve-leave-request/{leave_request_id}", tags=["leave-requests"])
async def approve_leave_request(
    leave_request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    """
    Mark a leave request as approved.

    :param leave_request_id: The id of the leave request to approve.
    :param current_user: The current user.
    :param session: The database session.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sussy activity detected.",
        )

    LeaveRequestService(session).set_leave_request_status(
        leave_request_id, LeaveRequestStatus.approved
    )


@router.put("/api/deny-leave-request/{leave_request_id}", tags=["leave-requests"])
async def deny_leave_request(
    leave_request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    """
    Mark a leave request as denied.

    :param leave_request_id: The id of the leave request to deny.
    :param current_user: The current user.
    :param session: The database session.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sussy activity detected.",
        )

    LeaveRequestService(session).set_leave_request_status(
        leave_request_id, LeaveRequestStatus.denied
    )
