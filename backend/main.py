
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="StudyMind AI API")

# Allow your GitHub Pages website to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nightrider99.github.io",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
            detail="Question is too long. Please shorten it."
        )

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "You are StudyMind AI, a friendly learning assistant. "
                "Explain concepts clearly for students. "
                "Use simple language and helpful examples. "
                "If you are unsure, say so."
            ),
            input=question,
        )

        return {"answer": response.output_text}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI request failed. Please try again later."
        )
