"""Base class for application services."""
from sqlmodel import Session


class SessionMixin:
    """Provide instance of database session."""

    def __init__(self: "SessionMixin", session: Session) -> None:
        """Initialize the session."""
        self.session = session


class BaseService(SessionMixin):
    """Base class for application services."""
