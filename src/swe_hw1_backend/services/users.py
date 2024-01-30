"""Module containing user database logic."""
from sqlmodel import select

from ..models.users import User
from ..services.base import BaseService


class UserService(BaseService):
    """Database services for users."""

    def create_user(self: "UserService", user: User) -> User:
        """
        Insert a new user into the database.

        :param user: The user object containing the user information.
        """
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def get_user_by_username(self: "UserService", username: str) -> User:
        """
        Query the database for a user by their username.

        :param username: The username to query.
        :return: `User` corresponding to the username or `None` if no user with that
        username exists.
        """
        query = select(User).where(User.username == username)
        result = self.session.exec(query).one_or_none()

        return result

    def increment_remaining_leave_days(
        self: "UserService", username: str, days: int
    ) -> None:
        """
        Increment the specified amount of days to user's remaining leave days.

        :param username: The username of the user to query.
        :param days: The number of days to increment.
        """
        user: User = self.get_user_by_username(username)
        user.remaining_leave_days += days
        self.session.add(user)
        self.session.commit()

    def deduct_remaining_leave_days(
        self: "UserService", username: str, days: int
    ) -> None:
        """
        Deducts the specified amount of days from user's remaining leave days.

        :param username: The username of the user to query.
        :param days: The number of days to deduct.
        """
        user: User = self.get_user_by_username(username)
        user.remaining_leave_days -= days
        self.session.add(user)
        self.session.commit()
