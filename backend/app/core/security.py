import time
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

_jwks: dict = {"keys": None, "at": 0.0}
_JWKS_TTL = 3600

def _get_jwks() -> dict:
    now = time.time()
    if _jwks["keys"] is None or now - _jwks["at"] > _JWKS_TTL:
        url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        _jwks["keys"], _jwks["at"] = r.json(), now
    return _jwks["keys"]

def get_current_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = creds.credentials
    try:
        header = jwt.get_unverified_header(token)
        key = next(
            (k for k in _get_jwks()["keys"] if k["kid"] == header.get("kid")), None
        )
        if key is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown signing key")
        payload = jwt.decode(
            token, key, algorithms=[header["alg"]], audience=settings.supabase_jwt_aud
        )
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {e}")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token missing sub")
    return sub
