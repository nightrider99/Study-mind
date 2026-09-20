from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    # Optional: restrict retrieval to specific documents. Empty = all user docs.
    document_ids: list[str] = []
    k: int = Field(default=6, ge=1, le=12)


class ChatSource(BaseModel):
    chunk_id: str
    document_id: str
    similarity: float
    snippet: str
