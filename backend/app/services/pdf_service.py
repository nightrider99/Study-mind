from io import BytesIO
from dataclasses import dataclass
from pypdf import PdfReader


@dataclass
class ParsedDoc:
    text: str
    page_count: int


def parse_pdf(data: bytes) -> ParsedDoc:
    reader = PdfReader(BytesIO(data))
    pages: list[str] = []
    for p in reader.pages:
        pages.append((p.extract_text() or "").strip())
    text = "\n\n".join(p for p in pages if p)
    return ParsedDoc(text=text, page_count=len(reader.pages))


def chunk_text(
    text: str, target_words: int = 600, overlap_words: int = 75
) -> list[str]:
    """Simple sliding-window chunker over whitespace tokens.

    ~600 words ≈ ~800 tokens, which plays nicely with text-embedding-004's
    2048-token input limit and keeps retrieval granularity useful.
    """
    words = text.split()
    if not words:
        return []
    target_words = max(50, target_words)
    overlap_words = max(0, min(overlap_words, target_words - 1))
    step = target_words - overlap_words

    chunks: list[str] = []
    for i in range(0, len(words), step):
        piece = words[i : i + target_words]
        if not piece:
            break
        chunks.append(" ".join(piece))
        if i + target_words >= len(words):
            break
    return chunks
