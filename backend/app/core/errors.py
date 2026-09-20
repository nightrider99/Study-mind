import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = logging.getLogger("studymind.errors")


class AppError(Exception):
    code = "INTERNAL"
    status_code = 500

    def __init__(self, message: str, *, code: str | None = None,
                 status_code: int | None = None, detail=None):
        super().__init__(message)
        self.message = message
        self.detail = detail
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class BadRequest(AppError):
    code, status_code = "BAD_REQUEST", 400


class Unauthorized(AppError):
    code, status_code = "UNAUTHORIZED", 401


class NotFound(AppError):
    code, status_code = "NOT_FOUND", 404


class RateLimited(AppError):
    code, status_code = "RATE_LIMITED", 429


class UpstreamError(AppError):
    """Gemini/Supabase/storage failure. Safe to surface, generic message."""
    code, status_code = "UPSTREAM_ERROR", 502


def _body(code: str, message: str, detail=None) -> dict:
    err: dict = {"code": code, "message": message}
    if detail is not None:
        err["detail"] = detail
    return {"error": err}


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    log.warning("app_error", extra={"extra_fields": {"code": exc.code, "msg": exc.message}})
    return JSONResponse(_body(exc.code, exc.message, exc.detail), status_code=exc.status_code)


async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        _body("VALIDATION_ERROR", "Invalid request", exc.errors()),
        status_code=422,
    )


async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled")
    return JSONResponse(_body("INTERNAL", "Internal server error"), status_code=500)
