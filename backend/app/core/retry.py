import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar

log = logging.getLogger("studymind.retry")
T = TypeVar("T")


def call_with_retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    base: float = 0.7,
    max_sleep: float = 8.0,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    label: str = "call",
) -> T:
    """Exponential backoff with jitter. Raises the final exception on exhaustion."""
    last: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except retry_on as e:
            last = e
            if i == attempts - 1:
                break
            sleep = min(max_sleep, base * (2 ** i)) * (0.5 + random.random())
            log.warning("retry", extra={"extra_fields": {
                "label": label, "attempt": i + 1, "sleep": round(sleep, 2),
                "err": str(e)[:200],
            }})
            time.sleep(sleep)
    assert last is not None
    raise last
