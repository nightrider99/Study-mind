from datetime import datetime
from pydantic import BaseModel, Field


class GenerateDeckRequest(BaseModel):
    document_ids: list[str] = []
    note_ids: list[str] = []
    num_cards: int = Field(default=15, ge=3, le=50)
    title: str | None = None


class CardOut(BaseModel):
    id: str
    front: str
    back: str
    due_at: datetime
    interval_days: float
    reps: int
    lapses: int
    ease: float


class DeckOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    card_count: int
    due_count: int


class DeckDetailOut(DeckOut):
    cards: list[CardOut]


class ReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=4)
