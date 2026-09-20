export type Note = {
  id: string;
  user_id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type Document = {
  id: string;
  user_id: string;
  filename: string;
  storage_path: string;
  mime_type: string | null;
  size_bytes: number | null;
  page_count: number | null;
  status: "processing" | "ready" | "failed";
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type ChatSource = {
  chunk_id: string;
  document_id: string;
  similarity: number;
  snippet: string;
};

export type ChatSession = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[] | null;
  created_at: string;
};

export type QuizSummary = {
  id: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
  created_at: string;
  question_count: number;
};

export type QuizQuestion = {
  id: string;
  order_index: number;
  question: string;
  options: string[];
  explanation: string | null;
};

export type QuizDetail = QuizSummary & { questions: QuizQuestion[] };

export type QuizResult = {
  score: number;
  total: number;
  correct_indices: number[];
  explanations: (string | null)[];
};

export type DeckSummary = {
  id: string;
  title: string;
  created_at: string;
  card_count: number;
  due_count: number;
};

export type Card = {
  id: string;
  front: string;
  back: string;
  due_at: string;
  interval_days: number;
  reps: number;
  lapses: number;
  ease: number;
};

export type DeckDetail = DeckSummary & { cards: Card[] };

export type ProgressSummary = {
  notes_count: number;
  documents_count: number;
  quizzes_taken: number;
  avg_score: number;
  cards_due: number;
  cards_total: number;
  streak_days: number;
};

export type TimelinePoint = {
  day: string;
  quiz_attempts: number;
  cards_reviewed: number;
  avg_score: number;
};
