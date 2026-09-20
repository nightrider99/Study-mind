from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    user_id: str
    filename: str
    storage_path: str
    mime_type: str | None = None
    size_bytes: int | None = None
    page_count: int | None = None
    status: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime
