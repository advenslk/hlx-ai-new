"""
HELZERX AI Support - Helper Utilities
Ticket ID generation, date formatting, string truncation, and Discord helpers.
"""
from __future__ import annotations

import random
import string
import datetime
from typing import Optional


def generate_ticket_id(category_prefix: str = "HZX") -> str:
    """
    Generates a unique, professional ticket reference ID.
    Example: HZX-8429, HZX-MC-1042
    """
    digits = "".join(random.choices(string.digits, k=4))
    return f"{category_prefix.upper()}-{digits}"


def format_iso_timestamp(dt: Optional[datetime.datetime] = None) -> str:
    """Returns an ISO 8601 formatted timestamp string."""
    dt = dt or datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def truncate(text: str, max_len: int = 100, suffix: str = "...") -> str:
    """Safely truncates string without breaking layout."""
    if not text or len(text) <= max_len:
        return text or ""
    return text[: max_len - len(suffix)] + suffix


def sanitize_channel_name(ticket_id: str, category: str, username: str) -> str:
    """
    Creates a clean, valid Discord text channel slug.
    Example: ticket-hzx-8429-minecraft
    """
    clean_cat = "".join(c for c in category.lower() if c.isalnum() or c == "-")[:8]
    clean_id = ticket_id.lower().replace("_", "-")
    clean_user = "".join(c for c in username.lower() if c.isalnum())[:10]
    return f"ticket-{clean_id}-{clean_cat}"
