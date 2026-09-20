import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.rate_limit import gemini_limiter
from app.core.security import get_current_user_id
from app.schemas.chat import ChatRequest, SessionDetailOut, SessionOut
from app.services import chat_service
from app.services.ai_service import stream_chat
from app.services.retrieval_service import search_chunks

router = APIRouter()

SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ---------- sessions ----------

@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user_id: str = Depends(get_current_user_id)):
    return chat_service.list_sessions(user_id)


@router.get("/sessions/{session_id}", response_model=SessionDetailOut)
def get_session(session_id: str, user_id: str = Depends(get_current_user_id)):
    sess = next(
        (s for s in chat_service.list_sessions(user_id) if s["id"] == session_id),
        None,
    )
    msgs = chat_service.get_session_messages(user_id, session_id)
    if sess is None or msgs is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return {**sess, "messages": msgs}


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str, user_id: str = Depends(get_current_user_id)):
    if not chat_service.delete_session(user_id, session_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")


# ---------- streaming ----------

@router.post("/stream")
def chat_stream(body: ChatRequest, user_id: str = Depends(get_current_user_id)):
    gemini_limiter.check(user_id)

    chunks = search_chunks(user_id=user_id, query=body.message, k=body.k)
    if body.document_ids:
        allowed = set(body.document_ids)
        chunks = [c for c in chunks if c["document_id"] in allowed]

    sources = [
        {
            "chunk_id": c["id"],
            "document_id": c["document_id"],
            "similarity": float(c.get("similarity", 0.0)),
            "snippet": c["content"][:280],
        }
        for c in chunks
    ]

    session_id: str | None = None
    history: list[dict] = []
    if body.session_id is not None:
        session_id = chat_service.get_or_create_session(
            user_id, body.session_id, body.message
        )
        history = chat_service.load_history(user_id, session_id)
        chat_service.append_message(user_id, session_id, "user", body.message)

    def gen() -> Iterator[str]:
        if session_id:
            yield _sse("session", {"session_id": session_id})
        yield _sse("sources", {"sources": sources})

        if not chunks:
            msg = ("I don't see anything in your materials about that. "
                   "Try uploading a document or rephrasing.")
            yield _sse("token", {"text": msg})
            if session_id:
                chat_service.append_message(user_id, session_id, "assistant", msg, sources)
            yield _sse("done", {"reason": "no_context"})
            return

        acc: list[str] = []
        try:
            for delta in stream_chat(body.message, chunks, history):
                acc.append(delta)
                yield _sse("token", {"text": delta})
            if session_id and acc:
                chat_service.append_message(
                    user_id, session_id, "assistant", "".join(acc), sources
                )
            yield _sse("done", {"reason": "stop"})
        except Exception:
            yield _sse("error", {"message": "Generation failed. Please retry."})
            yield _sse("done", {"reason": "error"})

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)
