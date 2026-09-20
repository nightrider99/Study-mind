from datetime import datetime
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = ""
    tags: list[str] = []

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None

class NoteOut(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
