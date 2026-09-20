from pydantic import BaseModel
from google import genai
from google.genai import types
from app.core.config import settings

_client: genai.Client | None = None


class _GenQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class _GenQuiz(BaseModel):
    title: str
    questions: list[_GenQuestion]


class _GenCard(BaseModel):
    front: str
    back: str


class _GenDeck(BaseModel):
    title: str
    cards: list[_GenCard]


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


QUIZ_INSTRUCTIONS = """You generate multiple-choice quiz questions from study material.

Rules:
- Every question must be answerable from the material alone.
- Exactly 4 options per question, exactly one correct.
- Distractors must be plausible but clearly wrong to someone who studied the material.
- Vary difficulty; prefer reasoning over trivial recall when the material allows.
- Explanations: 1-2 sentences, explain the reasoning, don't just restate the answer.
- Do NOT number questions in the 'question' field.
"""

DECK_INSTRUCTIONS = """You generate flashcards from study material.

Rules:
- One fact or concept per card.
- Front: a short, specific prompt (a term, a question, "What is X?").
- Back: a concise answer, 1-3 sentences max.
- No yes/no questions.
- Cover the key ideas; skip trivia and edge cases.
"""


def generate_quiz(source_text: str, num_questions: int, difficulty: str) -> dict:
    client = _get_client()
    prompt = (
        f"Difficulty: {difficulty}.\n"
        f"Generate exactly {num_questions} questions.\n\n"
        f"Study material:\n---\n{source_text}\n---"
    )
    resp = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=QUIZ_INSTRUCTIONS,
            temperature=0.6,
            response_mime_type="application/json",
            response_schema=_GenQuiz,
        ),
    )
    data = resp.parsed
    if data is None:
        raise RuntimeError("Gemini returned no parsed quiz")
    return data.model_dump()


def generate_deck(source_text: str, num_cards: int) -> dict:
    client = _get_client()
    prompt = (
        f"Generate exactly {num_cards} flashcards.\n\n"
        f"Study material:\n---\n{source_text}\n---"
    )
    resp = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=DECK_INSTRUCTIONS,
            temperature=0.5,
            response_mime_type="application/json",
            response_schema=_GenDeck,
        ),
    )
    data = resp.parsed
    if data is None:
        raise RuntimeError("Gemini returned no parsed deck")
    return data.model_dump()
