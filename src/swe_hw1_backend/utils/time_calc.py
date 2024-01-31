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


def date_from_iso_format(date: str) -> datetime:
    """Convert an ISO formatted date string to a datetime object."""
    return datetime.fromisoformat(date)


def is_two_months_in_advance(date: datetime) -> bool:
    """
    Check if a date is at least two months in advance.

    :param date: The date to check.
    :return: Whether the date is at least two months in advance.
    """
    today = datetime.now()
    return (date - today).days >= 60
