from datetime import datetime
from pydantic import BaseModel, Field


class GenerateQuizRequest(BaseModel):
    document_ids: list[str] = []
    note_ids: list[str] = []
    num_questions: int = Field(default=10, ge=3, le=30)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    title: str | None = None


class QuizQuestionOut(BaseModel):
    id: str
    order_index: int
    question: str
    options: list[str]
    explanation: str | None = None
    # correct_index intentionally omitted — returned only on submit


class QuizOut(BaseModel):
    id: str
    title: str
    difficulty: str
    created_at: datetime
    question_count: int


class QuizDetailOut(QuizOut):
    questions: list[QuizQuestionOut]


class SubmitQuizRequest(BaseModel):
    answers: list[int]   # selected option index per question, in order


class QuizResultOut(BaseModel):
    score: int
    total: int
    correct_indices: list[int]
    explanations: list[str | None]
