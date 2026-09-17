
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

app = FastAPI(title="StudyMind AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nightrider99.github.io",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "StudyMind AI API is running"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    if len(question) > 4000:
        raise HTTPException(
            status_code=400,
            detail="Question is too long."
        )

    if client is None:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "You are StudyMind AI, a friendly learning assistant. "
                "Explain concepts in simple language and give examples "
                "when helpful. If unsure, say so.\n\n"
                f"Student question: {question}"
            ),
        )

        return {"answer": response.text or "No answer was returned."}

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI request failed. Please try again."
        )
