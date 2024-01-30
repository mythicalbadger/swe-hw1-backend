"""SQLModel class for users."""
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    username: str = Field(index=True)
    hashed_password: bytes
    remaining_leave_days: int = Field(default=42)
    is_admin: bool = Field(default=False)
