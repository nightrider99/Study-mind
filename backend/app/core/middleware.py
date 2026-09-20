import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging import request_id_var

log = logging.getLogger("studymind.http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        start = time.monotonic()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        dur_ms = int((time.monotonic() - start) * 1000)
        response.headers["X-Request-ID"] = rid
        log.info("req", extra={"extra_fields": {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": dur_ms,
        }})
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Content-Length based. Doesn't catch chunked uploads — the upload route
    also reads-and-checks bytes, so this is a cheap first line of defense."""

    def __init__(self, app, max_bytes: int = 25 * 1024 * 1024):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl:
            try:
                if int(cl) > self.max_bytes:
                    return JSONResponse(
                        {"error": {"code": "PAYLOAD_TOO_LARGE",
                                   "message": f"Body exceeds {self.max_bytes} bytes"}},
                        status_code=413,
                    )
            except ValueError:
                return JSONResponse(
                    {"error": {"code": "BAD_REQUEST", "message": "Invalid Content-Length"}},
                    status_code=400,
                )
        return await call_next(request)
