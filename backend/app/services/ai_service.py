from collections.abc import Iterator
from google import genai
from google.genai import types
from app.core.config import settings

_client: genai.Client | None = None

SYSTEM_PROMPT = """You are StudyMind, a study assistant.

Rules:
- Answer ONLY using the provided context blocks.
- If the context does not contain the answer, say so plainly: "I don't see that in your materials." Do not guess or use outside knowledge.
- Cite sources inline using bracketed numbers that match the context block numbers, e.g. [1], [2].
- Be concise and direct. Prefer short paragraphs or bullet lists over long prose.
- When the question is a study query (definitions, relationships, "why"), explain clearly and give a one-line summary at the end.
"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _build_context_block(chunks: list[dict]) -> str:
    if not chunks:
        return "(no context available)"
    lines = []
    for i, c in enumerate(chunks, start=1):
        lines.append(f"[{i}] {c['content'].strip()}")
    return "\n\n".join(lines)


def stream_chat(
    user_message: str,
    chunks: list[dict],
    history: list[dict] | None = None,
) -> Iterator[str]:
    """Yield plain text deltas from Gemini. History is a list of
    {"role": "user"|"model", "text": "..."} dicts (stateless API — caller sends it)."""
    client = _get_client()

    context = _build_context_block(chunks)
    user_turn = (
        f"Context blocks:\n{context}\n\n"
        f"---\n\nQuestion: {user_message}"
    )

    contents: list[types.Content] = []
    for h in history or []:
        contents.append(
            types.Content(role=h["role"], parts=[types.Part(text=h["text"])])
        )
    contents.append(types.Content(role="user", parts=[types.Part(text=user_turn)]))

    stream = client.models.generate_content_stream(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )

    for event in stream:
        # event.text is None for some chunk shapes (safety blocks, empty parts)
        text = getattr(event, "text", None)
        if text:
            yield text
