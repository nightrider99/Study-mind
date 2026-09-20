import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.schemas.chat import ChatRequest
from app.services.ai_service import stream_chat
from app.services.retrieval_service import search_chunks

router = APIRouter()

SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",   # disable Render/nginx proxy buffering
}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
def chat_stream(
    body: ChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    chunks = search_chunks(
        user_id=user_id,
        query=body.message,
        k=body.k,
    )
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

    def gen() -> Iterator[str]:
        # 1) Sources first so the UI can render citations while text streams.
        yield _sse("sources", {"sources": sources})

        if not chunks:
            yield _sse(
                "token",
                {"text": "I don't see anything in your materials about that. "
                         "Try uploading a document or rephrasing."},
            )
            yield _sse("done", {"reason": "no_context"})
            return

        try:
            for delta in stream_chat(body.message, chunks):
                yield _sse("token", {"text": delta})
            yield _sse("done", {"reason": "stop"})
        except Exception as e:
            yield _sse("error", {"message": str(e)})
            yield _sse("done", {"reason": "error"})

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)
