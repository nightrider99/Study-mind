from datetime import date, datetime, timedelta, timezone

from app.database.connection import get_supabase


def _count(table: str, user_id: str, **eq) -> int:
    sb = get_supabase()
    q = sb.table(table).select("id", count="exact").eq("user_id", user_id)
    for k, v in eq.items():
        q = q.eq(k, v)
    return q.execute().count or 0


def _compute_streak(user_id: str, lookback_days: int = 90) -> int:
    """Consecutive days (ending today or yesterday) with >= 1 study event."""
    sb = get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    rows = (
        sb.table("study_events").select("created_at")
        .eq("user_id", user_id).gte("created_at", since)
        .execute().data or []
    )
    days = {(datetime.fromisoformat(r["created_at"]).date()) for r in rows}
    if not days:
        return 0

    today = datetime.now(timezone.utc).date()
    # allow streak to be "alive" if last study was today or yesterday
    cursor = today if today in days else today - timedelta(days=1)
    if cursor not in days:
        return 0

    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def get_summary(user_id: str) -> dict:
    sb = get_supabase()
    now_iso = datetime.now(timezone.utc).isoformat()

    notes_count = _count("notes", user_id)
    documents_count = _count("documents", user_id, status="ready")
    quizzes_taken = _count("quiz_attempts", user_id)

    # avg score as percent
    attempts = (
        sb.table("quiz_attempts").select("score, total")
        .eq("user_id", user_id).execute().data or []
    )
    if attempts:
        pct_sum = sum((a["score"] / a["total"] * 100.0) for a in attempts if a["total"])
        avg_score = round(pct_sum / len(attempts), 1)
    else:
        avg_score = 0.0

    cards = (
        sb.table("flashcards").select("due_at")
        .eq("user_id", user_id).execute().data or []
    )
    cards_total = len(cards)
    cards_due = sum(1 for c in cards if c["due_at"] <= now_iso)

    return {
        "notes_count": notes_count,
        "documents_count": documents_count,
        "quizzes_taken": quizzes_taken,
        "avg_score": avg_score,
        "cards_due": cards_due,
        "cards_total": cards_total,
        "streak_days": _compute_streak(user_id),
    }


def get_timeline(user_id: str, days: int = 30) -> list[dict]:
    sb = get_supabase()
    res = sb.rpc(
        "progress_timeline",
        {"p_user_id": user_id, "p_days": days},
    ).execute()
    return res.data or []


def log_event(user_id: str, kind: str, ref_id: str | None, value: float | None) -> None:
    sb = get_supabase()
    sb.table("study_events").insert({
        "user_id": user_id,
        "kind": kind,
        "ref_id": ref_id,
        "value": value,
    }).execute()
