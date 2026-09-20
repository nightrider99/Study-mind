from app.database.connection import get_supabase


def _round_robin(groups: list[list[str]]) -> list[str]:
    """Interleave groups so a multi-doc request doesn't get dominated by one doc."""
    out: list[str] = []
    i = 0
    while True:
        added = False
        for g in groups:
            if i < len(g):
                out.append(g[i])
                added = True
        if not added:
            break
        i += 1
    return out


def build_source_text(
    user_id: str,
    document_ids: list[str],
    note_ids: list[str],
    max_words: int = 6000,
) -> str:
    sb = get_supabase()
    parts: list[str] = []

    if document_ids:
        rows = (
            sb.table("chunks").select("document_id, chunk_index, content")
            .in_("document_id", document_ids).eq("user_id", user_id)
            .order("chunk_index").execute().data or []
        )
        by_doc: dict[str, list[str]] = {}
        for r in rows:
            by_doc.setdefault(r["document_id"], []).append(r["content"])
        merged = _round_robin(list(by_doc.values()))
        if merged:
            parts.append("\n\n".join(merged))

    if note_ids:
        rows = (
            sb.table("notes").select("title, content")
            .in_("id", note_ids).eq("user_id", user_id).execute().data or []
        )
        for n in rows:
            parts.append(f"# {n['title']}\n{n['content']}")

    text = "\n\n---\n\n".join(p for p in parts if p.strip())
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return text
