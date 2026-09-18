import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, Field

app = FastAPI(title="StudyMind AI API", version="1.0.0")


def get_allowed_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "")
    defaults = {
        "https://nightrider99.github.io",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    }
    defaults.update(origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip())
    return sorted(defaults)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)


def get_client() -> Optional[genai.Client]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return genai.Client(api_key=api_key) if api_key else None


@app.get("/")
def home():
    return {"message": "StudyMind AI API is running", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("GEMINI_API_KEY", "").strip())}


@app.post("/ask")
@app.post("/api/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please enter a question.")

    client = get_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Set GEMINI_API_KEY on the backend."
        )

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=(
                "You are StudyMind AI, a friendly learning assistant. "
                "Explain concepts in simple language, use examples when helpful, "
                "and say when you are uncertain.\n\n"
                f"Student question: {question}"
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("The AI returned an empty response")
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as exc:
        # Do not expose provider credentials or internal details to the browser.
        print(f"Gemini request failed: {exc}")
        raise HTTPException(status_code=502, detail="AI request failed. Please try again.")
