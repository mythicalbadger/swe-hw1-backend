"""This module contains services for leave requests."""
from typing import List

from sqlmodel import select

from ..models.leave_requests import LeaveRequest, LeaveRequestStatus
from ..services.base import BaseService


class LeaveRequestService(BaseService):
    """Database services for leave requests."""

    def create_leave_request(
        self: "LeaveRequestService", leave_request: LeaveRequest
    ) -> None:
        """
        Insert a new leave request into the database.

        :param leave_request: The leave request object containing user information.
        """
        self.session.add(leave_request)
        self.session.commit()

    def get_leave_requests_by_requester_id(
        self: "LeaveRequestService", requester_id: int
    ) -> List[LeaveRequest]:
        """
        Get all leave requests for user with the given id.

        :param requester_id: The id of the user to get the leave requests for.
        :return: A list of leave requests for the given id.
        """
        query = select(LeaveRequest).where(LeaveRequest.requester_id == requester_id)
        result: List[LeaveRequest] = self.session.exec(query).all()

        return result

    def get_leave_request_by_id(self: "LeaveRequestService", id: int) -> LeaveRequest:
        """
        Get a leave request with the given id.

        :param id: The id of the leave request to query.
        :return: The leave request with given id.
        """
        query = select(LeaveRequest).where(LeaveRequest.id == id)
        result: LeaveRequest = self.session.exec(query).one()

        return result

    def get_all_leave_requests(self: "LeaveRequestService") -> List[LeaveRequest]:
        """
        Fetch all leave requests created.

        :return: A list of all leave requests ordered by start date.
        """
        query = select(LeaveRequest)
        result: List[LeaveRequest] = self.session.exec(query).all()

        return result

    def delete_leave_request(
        self: "LeaveRequestService", leave_request_id: int
    ) -> None:
        """
        Delete a leave request.

        :param leave_request_id: The id of the leave request to delete.
        """
        leave_request = self.get_leave_request_by_id(leave_request_id)
        self.session.delete(leave_request)
        self.session.commit()

    def set_leave_request_status(
        self: "LeaveRequestService", leave_request_id: int, status: LeaveRequestStatus
    ) -> None:
        """
        Set the status of a leave request.

        :param leave_request_id: The id of the leave request to set.
        :param status: The status to set.
        """
        leave_request = self.get_leave_request_by_id(leave_request_id)
        leave_request.status = status
        self.session.add(leave_request)
        self.session.commit()
