import { apiFetch } from "./api";
import type { DeckSummary, DeckDetail, Card } from "../types";

export const flashcardsApi = {
  listDecks: () => apiFetch<DeckSummary[]>("/api/v1/flashcards/decks"),
  getDeck: (id: string) => apiFetch<DeckDetail>(`/api/v1/flashcards/decks/${id}`),
  generate: (body: {
    document_ids?: string[];
    note_ids?: string[];
    num_cards?: number;
    title?: string;
  }) => apiFetch<DeckDetail>("/api/v1/flashcards/decks/generate", { method: "POST", body: JSON.stringify(body) }),
  due: (deckId?: string, limit = 50) =>
    apiFetch<Card[]>(`/api/v1/flashcards/due?${new URLSearchParams({ ...(deckId ? { deck_id: deckId } : {}), limit: String(limit) })}`),
  review: (cardId: string, rating: 1 | 2 | 3 | 4) =>
    apiFetch<Card>(`/api/v1/flashcards/cards/${cardId}/review`, { method: "POST", body: JSON.stringify({ rating }) }),
  removeDeck: (id: string) => apiFetch<void>(`/api/v1/flashcards/decks/${id}`, { method: "DELETE" }),
};
