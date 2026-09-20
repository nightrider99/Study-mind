from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, status


class RateLimiter:
    """In-memory sliding-window limiter. Per-worker only — good enough for a
    single Render instance on the free tier. Swap for Redis if you scale out."""

    def __init__(self, max_per_window: int = 12, window_seconds: int = 60):
        self.max = max_per_window
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.max:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Rate limit reached — slow down for a moment.",
                )
            q.append(now)


gemini_limiter = RateLimiter(max_per_window=12, window_seconds=60)
