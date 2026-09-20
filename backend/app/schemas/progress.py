from datetime import date
from pydantic import BaseModel


class ProgressSummary(BaseModel):
    notes_count: int
    documents_count: int
    quizzes_taken: int
    avg_score: float          # 0-100, 0 if no attempts
    cards_due: int
    cards_total: int
    streak_days: int


class TimelinePoint(BaseModel):
    day: date
    quiz_attempts: int
    cards_reviewed: int
    avg_score: float


class TimelineOut(BaseModel):
    days: list[TimelinePoint]
