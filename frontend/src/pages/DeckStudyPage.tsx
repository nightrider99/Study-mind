import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { flashcardsApi } from "../services/flashcards";
import { Spinner } from "../components/common/Spinner";
import { ErrorBanner } from "../components/common/ErrorBanner";
import { useToast } from "../hooks/useToast";
import type { Card } from "../types";

export default function DeckStudyPage() {
  const { deckId } = useParams<{ deckId: string }>();
  const [cards, setCards] = useState<Card[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [err, setErr] = useState<Error | null>(null);
  const [busy, setBusy] = useState(false);
  const { push } = useToast();

  useEffect(() => {
    if (!deckId) return;
    flashcardsApi.due(deckId)
      .then(setCards)
      .catch((e) => setErr(e instanceof Error ? e : new Error(String(e))));
  }, [deckId]);

  async function rate(rating: 1 | 2 | 3 | 4) {
    if (!cards) return;
    const card = cards[idx];
    setBusy(true);
    try {
      await flashcardsApi.review(card.id, rating);
      if (idx + 1 >= cards.length) {
        push("success", "Session complete 🎉");
        setCards([]);
      } else {
        setIdx((i) => i + 1);
        setFlipped(false);
      }
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Review failed");
    } finally {
      setBusy(false);
    }
  }

  if (err) return <ErrorBanner error={err} />;
  if (!cards) return <Spinner />;

  if (cards.length === 0) {
    return (
      <>
        <div className="page-head">
          <h1>Study complete</h1>
          <Link to="/flashcards" className="btn">Back to decks</Link>
        </div>
        <div className="empty">You've reviewed all due cards in this deck.</div>
      </>
    );
  }

  const card = cards[idx];

  return (
    <>
      <div className="page-head">
        <h1>Study</h1>
        <div className="row">
          <span className="muted">{idx + 1} / {cards.length}</span>
          <Link to="/flashcards" className="btn ghost">Exit</Link>
        </div>
      </div>

      <div className={`flashcard ${flipped ? "flipped" : ""}`} onClick={() => setFlipped((f) => !f)}>
        <div className="flashcard-inner">
          <div className="flashcard-face">{card.front}</div>
          <div className="flashcard-face back">{card.back}</div>
        </div>
      </div>

      <div className="row" style={{ justifyContent: "center", marginTop: 20, gap: 10 }}>
        {!flipped
          ? <button className="btn primary" onClick={() => setFlipped(true)}>Show answer</button>
          : (
            <>
              <button className="btn danger" disabled={busy} onClick={() => rate(1)}>Again</button>
              <button className="btn" disabled={busy} onClick={() => rate(2)}>Hard</button>
              <button className="btn primary" disabled={busy} onClick={() => rate(3)}>Good</button>
              <button className="btn" disabled={busy} onClick={() => rate(4)}>Easy</button>
            </>
          )}
      </div>
    </>
  );
}
