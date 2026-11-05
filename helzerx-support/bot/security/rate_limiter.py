"""
HELZERX AI Support - Rate Limiter
Prevents spam and API exhaustion per Discord user and per ticket channel.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple


class SlidingWindowRateLimiter:
    """Sliding-window in-memory rate limiter."""

    def __init__(self, limit_per_minute: int = 6):
        self.limit = limit_per_minute
        self.window_seconds = 60
        self._user_timestamps: Dict[int, Deque[float]] = defaultdict(deque)

    def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """
        Checks if the user is allowed to send a message.
        Returns:
            (is_allowed: bool, retry_after_seconds: int)
        """
        now = time.time()
        timestamps = self._user_timestamps[user_id]

        # Evict timestamps outside the window
        while timestamps and timestamps[0] <= now - self.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= self.limit:
            oldest = timestamps[0]
            retry_after = int((oldest + self.window_seconds) - now) + 1
            return False, max(1, retry_after)

        timestamps.append(now)
        return True, 0

    def reset_user(self, user_id: int) -> None:
        """Clears the rate limit window for a user."""
        if user_id in self._user_timestamps:
            del self._user_timestamps[user_id]


rate_limiter = SlidingWindowRateLimiter(limit_per_minute=6)
