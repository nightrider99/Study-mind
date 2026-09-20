from datetime import datetime, timezone

from app.database.connection import get_supabase

HISTORY_TURNS = 6   # last 6 user/assistant pairs → 12 messages


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_or_create_session(user_id: str, session_id: str | None, first_message: str) -> str:
    sb = get_supabase()
    if session_id:
        rows = (
            sb.table("chat_sessions").select("id")
            .eq("id", session_id).eq("user_id", user_id).execute().data
        )
        if rows:
            return session_id
        # session_id provided but not owned/doesn't exist → fall through and create
    title = (first_message.strip()[:60] or "New chat").strip()
    row = (
        sb.table("chat_sessions").insert({"user_id": user_id, "title": title})
        .execute().data[0]
    )
    return row["id"]


def load_history(user_id: str, session_id: str, limit: int = HISTORY_TURNS * 2) -> list[dict]:
    sb = get_supabase()
    rows = (
        sb.table("chat_messages").select("role, content, created_at")
        .eq("session_id", session_id).eq("user_id", user_id)
        .order("created_at", desc=True).limit(limit).execute().data or []
    )
    rows.reverse()   # oldest → newest for Gemini
    return [{"role": r["role"], "text": r["content"]} for r in rows]


def append_message(user_id: str, session_id: str, role: str,
                   content: str, sources: list | None = None) -> None:
    sb = get_supabase()
    sb.table("chat_messages").insert({
        "session_id": session_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "sources": sources or [],
    }).execute()
    sb.table("chat_sessions").update({"updated_at": _now()}).eq("id", session_id).execute()


def list_sessions(user_id: str) -> list[dict]:
    sb = get_supabase()
    return (
        sb.table("chat_sessions").select("*")
        .eq("user_id", user_id).order("updated_at", desc=True).limit(50)
        .execute().data or []
    )


def get_session_messages(user_id: str, session_id: str) -> list[dict] | None:
    sb = get_supabase()
    owns = (
        sb.table("chat_sessions").select("id")
        .eq("id", session_id).eq("user_id", user_id).execute().data
    )
    if not owns:
        return None
    return (
        sb.table("chat_messages").select("*")
        .eq("session_id", session_id).eq("user_id", user_id)
        .order("created_at").execute().data or []
    )


def delete_session(user_id: str, session_id: str) -> bool:
    sb = get_supabase()
    res = (
        sb.table("chat_sessions").delete()
        .eq("id", session_id).eq("user_id", user_id).execute()
    )
    return bool(res.data)
