from google import genai
from google.genai import types

from app.core.config import settings
from app.core.retry import call_with_retry

_client: genai.Client | None = None
_BATCH = 50


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    client = _get_client()
    out: list[list[float]] = []
    for i in range(0, len(texts), _BATCH):
        batch = texts[i : i + _BATCH]
        resp = call_with_retry(
            lambda: client.models.embed_content(
                model=settings.embedding_model,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            ),
            label="embed_documents",
        )
        out.extend(list(e.values) for e in resp.embeddings)
    return out


def embed_query(text: str) -> list[float]:
    client = _get_client()
    resp = call_with_retry(
        lambda: client.models.embed_content(
            model=settings.embedding_model,
            contents=[text],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        ),
        label="embed_query",
    )
    return list(resp.embeddings[0].values)


def to_pgvector(emb: list[float]) -> str:
    """pgvector's text form. PostgREST cannot coerce a JSON array -> vector."""
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
