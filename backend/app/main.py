from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import (
    AppError, app_error_handler, unhandled_handler, validation_handler,
)
from app.core.logging import setup_logging
from app.core.middleware import BodySizeLimitMiddleware, RequestContextMiddleware

from app.api.routes import (
    chat, documents, flashcards, notes, progress, quizzes,
)

setup_logging()

app = FastAPI(title="StudyMind AI", version="0.1.0")

app.add_middleware(RequestContextMiddleware)
app.add_middleware(BodySizeLimitMiddleware, max_bytes=25 * 1024 * 1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(Exception, unhandled_handler)

for r, prefix, tag in [
    (notes.router,       "/api/v1/notes",       "notes"),
    (documents.router,   "/api/v1/documents",   "documents"),
    (chat.router,        "/api/v1/chat",        "chat"),
    (quizzes.router,     "/api/v1/quizzes",     "quizzes"),
    (flashcards.router,  "/api/v1/flashcards",  "flashcards"),
    (progress.router,    "/api/v1/progress",    "progress"),
]:
    app.include_router(r, prefix=prefix, tags=[tag])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/deep")
def health_deep():
    from app.database.connection import get_supabase
    checks: dict[str, str] = {}
    try:
        get_supabase().table("notes").select("id", count="exact").limit(1).execute()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"fail: {type(e).__name__}"
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
