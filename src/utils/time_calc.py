"""Utility functions for time calculations."""
from datetime import datetime


def days_between(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate the number of days between two dates.

    :param start_date: The first date.
    :param end_date: The second date.
    :return:
    """
    return (end_date - start_date).days + 1
