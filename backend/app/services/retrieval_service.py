from app.database.connection import get_supabase
from app.services.embedding_service import embed_query


def search_chunks(
    user_id: str,
    query: str,
    k: int = 6,
    min_similarity: float = 0.25,
) -> list[dict]:
    q = embed_query(query)
    sb = get_supabase()
    res = sb.rpc(
        "match_chunks",
        {
            "query_embedding": q,          # list[float] -> float8[]
            "match_user_id": user_id,
            "match_count": k,
            "min_similarity": min_similarity,
        },
    ).execute()
    return res.data or []
