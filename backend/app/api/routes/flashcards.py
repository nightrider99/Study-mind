from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user_id
from app.database.connection import get_supabase
from app.schemas.flashcard import (
    CardOut, DeckDetailOut, DeckOut,
    GenerateDeckRequest, ReviewRequest,
)
from app.services.generation_service import generate_deck
from app.services.source_service import build_source_text
from app.services.srs_service import apply_review

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_deck(deck_id: str, user_id: str) -> dict:
    sb = get_supabase()
    rows = (
        sb.table("decks").select("*")
        .eq("id", deck_id).eq("user_id", user_id).execute().data
    )
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deck not found")
    deck = rows[0]
    cards = (
        sb.table("flashcards").select("*")
        .eq("deck_id", deck_id).order("created_at").execute().data or []
    )
    now = _now_iso()
    due = sum(1 for c in cards if c["due_at"] <= now)
    return {**deck, "card_count": len(cards), "due_count": due, "cards": cards}


@router.post("/decks/generate", response_model=DeckDetailOut, status_code=201)
def create_deck(body: GenerateDeckRequest, user_id: str = Depends(get_current_user_id)):
    source = build_source_text(user_id, body.document_ids, body.note_ids)
    if not source.strip():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No source material — pass document_ids or note_ids with content",
        )

    try:
        generated = generate_deck(source, body.num_cards)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Generation failed: {e}")

    cards = generated.get("cards") or []
    if not cards:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Generator returned no cards")

    sb = get_supabase()
    title = body.title or generated.get("title") or "Untitled deck"
    deck = sb.table("decks").insert({
        "user_id": user_id,
        "title": title,
        "document_ids": body.document_ids,
        "note_ids": body.note_ids,
    }).execute().data[0]

    rows = [
        {
            "deck_id": deck["id"],
            "user_id": user_id,
            "front": str(c.get("front", "")).strip(),
            "back": str(c.get("back", "")).strip(),
        }
        for c in cards
        if c.get("front") and c.get("back")
    ]
    if rows:
        sb.table("flashcards").insert(rows).execute()

    return _load_deck(deck["id"], user_id)


@router.get("/decks", response_model=list[DeckOut])
def list_decks(user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    decks = (
        sb.table("decks").select("*")
        .eq("user_id", user_id).order("created_at", desc=True).execute().data or []
    )
    now = _now_iso()
    out = []
    for d in decks:
        cards = (
            sb.table("flashcards").select("due_at")
            .eq("deck_id", d["id"]).execute().data or []
        )
        due = sum(1 for c in cards if c["due_at"] <= now)
        out.append({**d, "card_count": len(cards), "due_count": due})
    return out


@router.get("/decks/{deck_id}", response_model=DeckDetailOut)
def get_deck(deck_id: str, user_id: str = Depends(get_current_user_id)):
    return _load_deck(deck_id, user_id)


@router.get("/due", response_model=list[CardOut])
def due_cards(
    deck_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
):
    sb = get_supabase()
    q = (
        sb.table("flashcards").select("*")
        .eq("user_id", user_id).lte("due_at", _now_iso())
        .order("due_at").limit(limit)
    )
    if deck_id:
        q = q.eq("deck_id", deck_id)
    return q.execute().data or []


@router.post("/cards/{card_id}/review", response_model=CardOut)
def review_card(
    card_id: str,
    body: ReviewRequest,
    user_id: str = Depends(get_current_user_id),
):
    sb = get_supabase()
    rows = (
        sb.table("flashcards").select("*")
        .eq("id", card_id).eq("user_id", user_id).execute().data
    )
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")
    card = rows[0]

    updates = apply_review(
        ease=float(card["ease"]),
        interval_days=float(card["interval_days"]),
        reps=int(card["reps"]),
        lapses=int(card["lapses"]),
        rating=body.rating,
    )
    sb.table("flashcards").update(updates).eq("id", card_id).execute()
    sb.table("flashcard_reviews").insert({
        "card_id": card_id,
        "user_id": user_id,
        "rating": body.rating,
    }).execute()

    return (
        sb.table("flashcards").select("*").eq("id", card_id).execute().data[0]
    )


@router.delete("/decks/{deck_id}", status_code=204)
def delete_deck(deck_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("decks").delete()
        .eq("id", deck_id).eq("user_id", user_id).execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deck not found")

     from app.services.progress_service import log_event
log_event(user_id, "card_review", card_id, float(body.rating))
