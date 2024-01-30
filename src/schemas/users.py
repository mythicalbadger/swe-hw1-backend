"""Schemas for users."""
from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating a user."""

    full_name: str
    username: str
    password: str
