from datetime import datetime, timedelta, timezone


def apply_review(
    ease: float,
    interval_days: float,
    reps: int,
    lapses: int,
    rating: int,
) -> dict:
    """SM-2-inspired scheduler with a 4-button UI.

    rating: 1 = again, 2 = hard, 3 = good, 4 = easy.
    Returns the fields to write back to the card row.
    """
    now = datetime.now(timezone.utc)

    if rating == 1:  # again — relearn today
        reps = 0
        lapses += 1
        ease = max(1.3, ease - 0.20)
        interval_days = 0.0
        due = now + timedelta(minutes=10)
    elif rating == 2:  # hard
        ease = max(1.3, ease - 0.15)
        interval_days = max(1.0, interval_days * 1.2) if interval_days > 0 else 1.0
        reps += 1
        due = now + timedelta(days=interval_days)
    elif rating == 3:  # good
        if interval_days == 0:
            interval_days = 1.0
        elif interval_days == 1.0:
            interval_days = 3.0
        else:
            interval_days = interval_days * ease
        reps += 1
        due = now + timedelta(days=interval_days)
    else:  # easy
        ease = min(3.0, ease + 0.15)
        interval_days = 3.0 if interval_days == 0 else interval_days * ease * 1.3
        reps += 1
        due = now + timedelta(days=interval_days)

    return {
        "ease": round(ease, 2),
        "interval_days": round(interval_days, 2),
        "reps": reps,
        "lapses": lapses,
        "due_at": due.isoformat(),
        "last_reviewed_at": now.isoformat(),
    }
