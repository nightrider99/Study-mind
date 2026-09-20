from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    document_ids: list[str] = []
    k: int = Field(default=6, ge=1, le=12)
    session_id: str | None = None       # omit for stateless


class ChatSource(BaseModel):
    chunk_id: str
    document_id: str
    similarity: float
    snippet: str


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: list[dict] | None = None
    created_at: datetime


class SessionDetailOut(SessionOut):
    messages: list[MessageOut]
