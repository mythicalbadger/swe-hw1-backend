"""Schemas for leave requests."""
from datetime import datetime

from pydantic import BaseModel


class LeaveRequestCreate(BaseModel):
    """Schema for creating leave request."""

    start_date: datetime
    end_date: datetime
    reason: str
