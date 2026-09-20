from fastapi import APIRouter, Depends, HTTPException, status

from app.core.rate_limit import gemini_limiter
from app.core.security import get_current_user_id
from app.database.connection import get_supabase
from app.schemas.quiz import (
    GenerateQuizRequest, QuizDetailOut, QuizOut, QuizQuestionOut,
    QuizResultOut, SubmitQuizRequest,
)
from app.services.generation_service import generate_quiz
from app.services.progress_service import log_event
from app.services.source_service import build_source_text

router = APIRouter()


def _load_detail(quiz_id: str, user_id: str) -> dict:
    sb = get_supabase()
    rows = (
        sb.table("quizzes").select("*")
        .eq("id", quiz_id).eq("user_id", user_id).execute().data
    )
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quiz not found")
    quiz = rows[0]
    qs = (
        sb.table("quiz_questions").select("*")
        .eq("quiz_id", quiz_id).order("order_index").execute().data or []
    )
    return {
        **quiz,
        "question_count": len(qs),
        "questions": [
            {
                "id": r["id"],
                "order_index": r["order_index"],
                "question": r["question"],
                "options": r["options"],
                "explanation": r.get("explanation"),
            }
            for r in qs
        ],
    }


@router.post("/generate", response_model=QuizDetailOut, status_code=201)
def create_quiz(body: GenerateQuizRequest, user_id: str = Depends(get_current_user_id)):
    gemini_limiter.check(user_id)

    source = build_source_text(user_id, body.document_ids, body.note_ids)
    if not source.strip():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No source material — pass document_ids or note_ids with content",
        )

    try:
        generated = generate_quiz(source, body.num_questions, body.difficulty)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Generation failed: {e}")

    questions = generated.get("questions") or []
    if not questions:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Generator returned no questions")

    sb = get_supabase()
    title = body.title or generated.get("title") or "Untitled quiz"
    quiz = sb.table("quizzes").insert({
        "user_id": user_id,
        "title": title,
        "difficulty": body.difficulty,
        "document_ids": body.document_ids,
        "note_ids": body.note_ids,
    }).execute().data[0]

    rows = []
    for i, q in enumerate(questions):
        opts = [str(o) for o in (q.get("options") or [])][:4]
        while len(opts) < 4:
            opts.append("")
        ci = int(q.get("correct_index", 0))
        if not 0 <= ci < 4:
            ci = 0
        rows.append({
            "quiz_id": quiz["id"],
            "order_index": i,
            "question": str(q.get("question", "")).strip(),
            "options": opts,
            "correct_index": ci,
            "explanation": q.get("explanation"),
        })
    sb.table("quiz_questions").insert(rows).execute()

    return _load_detail(quiz["id"], user_id)


@router.get("", response_model=list[QuizOut])
def list_quizzes(user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    quizzes = (
        sb.table("quizzes").select("*")
        .eq("user_id", user_id).order("created_at", desc=True).execute().data or []
    )
    out = []
    for q in quizzes:
        cnt = (
            sb.table("quiz_questions").select("id", count="exact")
            .eq("quiz_id", q["id"]).execute().count or 0
        )
        out.append({**q, "question_count": cnt})
    return out


@router.get("/{quiz_id}", response_model=QuizDetailOut)
def get_quiz(quiz_id: str, user_id: str = Depends(get_current_user_id)):
    return _load_detail(quiz_id, user_id)


@router.post("/{quiz_id}/submit", response_model=QuizResultOut)
def submit_quiz(
    quiz_id: str,
    body: SubmitQuizRequest,
    user_id: str = Depends(get_current_user_id),
):
    sb = get_supabase()
    owns = (
        sb.table("quizzes").select("id")
        .eq("id", quiz_id).eq("user_id", user_id).execute().data
    )
    if not owns:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quiz not found")

    qs = (
        sb.table("quiz_questions").select("*")
        .eq("quiz_id", quiz_id).order("order_index").execute().data or []
    )
    if len(body.answers) != len(qs):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Expected {len(qs)} answers, got {len(body.answers)}",
        )

    correct = [r["correct_index"] for r in qs]
    score = sum(1 for a, c in zip(body.answers, correct) if a == c)

    sb.table("quiz_attempts").insert({
        "quiz_id": quiz_id,
        "user_id": user_id,
        "score": score,
        "total": len(qs),
        "answers": body.answers,
    }).execute()

    pct = (score / len(qs) * 100.0) if qs else 0.0
    log_event(user_id, "quiz_attempt", quiz_id, pct)

    return {
        "score": score,
        "total": len(qs),
        "correct_indices": correct,
        "explanations": [r.get("explanation") for r in qs],
    }


@router.delete("/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("quizzes").delete()
        .eq("id", quiz_id).eq("user_id", user_id).execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quiz not found")
