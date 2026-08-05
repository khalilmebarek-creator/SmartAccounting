"""License expiry handling: grace period (14 days) then read-only mode.

Time handling is injected (``today``) so tests are deterministic and the
real clock is only touched by :func:`days_remaining` and :func:`expiry_from_today`.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

GRACE_DAYS = 14


def parse_expiry(value: str | date) -> date:
    """Parse an ISO date string (``YYYY-MM-DD``) or pass a date through."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_remaining(expiry: str | date, today: Optional[date] = None) -> int:
    """Days left until expiry (negative once past)."""
    exp = parse_expiry(expiry)
    ref = today if today is not None else date.today()
    return (exp - ref).days


def is_expired(expiry: str | date, today: Optional[date] = None) -> bool:
    """True once the expiry date has passed."""
    return days_remaining(expiry, today) < 0


def in_grace(expiry: str | date, today: Optional[date] = None) -> bool:
    """True if expired but still inside the grace period."""
    remaining = days_remaining(expiry, today)
    return remaining < 0 <= remaining + GRACE_DAYS


def is_read_only(expiry: str | date, today: Optional[date] = None) -> bool:
    """True once expired AND past the grace period (read-only mode)."""
    remaining = days_remaining(expiry, today)
    return remaining + GRACE_DAYS < 0


def expiry_from_today(days: int, today: Optional[date] = None) -> str:
    """ISO expiry date ``days`` from today (helper for key generation)."""
    ref = today if today is not None else date.today()
    return (ref + timedelta(days=days)).isoformat()
