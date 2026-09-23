# StudyMind AI

An AI-powered study assistant that turns your notes and documents into interactive learning tools — chat with your material, auto-generate quizzes and flashcards, and track your progress over time.

## Features

- 📝 **Notes** — create, organize, and manage study notes
- 📄 **Documents** — upload PDFs to use as study material
- 💬 **Chat** — ask questions and get answers grounded in your own notes/documents
- ❓ **Quizzes** — auto-generated multiple-choice quizzes from your material
- 🗂️ **Flashcards** — auto-generated with SM-2 spaced repetition
- 📊 **Progress** — track streaks, scores, and daily activity

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TypeScript |
| Backend | FastAPI (Python 3.11) in Docker |
| Database + Auth + Storage | Supabase (Postgres + pgvector) |
| AI | Google Gemini (`gemini-1.5-flash` + `text-embedding-004`) |
| Hosting | Vercel (frontend) + Render (backend) |
| Uptime | UptimeRobot |

All services used are on free tiers.

## Live URLs

- **App:** https://frontend-pdri.vercel.app
- **API:** https://studymind-api-7d17.onrender.com
- **API Docs:** https://studymind-api-7d17.onrender.com/docs

## Project Structure

```

Study-mind/
├── backend/           FastAPI app (Docker-deployed on Render)
│   └── app/
│       ├── api/routes/    notes, documents, chat, quizzes, flashcards, progress
│       ├── core/          config, security, errors, logging, middleware, rate_limit, retry
│       ├── database/      connection + migrations (001–006)
│       ├── schemas/       Pydantic models
│       └── services/      ai, embedding, generation, pdf, retrieval, srs, source, chat, progress
├── frontend/          React + Vite + TypeScript (Vercel)
│   └── src/
│       ├── components/    common, layout
│       ├── hooks/         useAuth, useAsync, useToast
│       ├── pages/         Login, Dashboard, Notes, Chat, Quiz, QuizRunner, Flashcards, DeckStudy, Progress
│       ├── services/      api client + per-domain wrappers
│       └── types/         shared TypeScript types
└── render.yaml        Render Blueprint

```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase + Gemini keys
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

Frontend

```bash
cd frontend
npm install
cp .env.example .env   # fill in API URL + Supabase keys
npm run dev
# → http://localhost:5173
```

Environment Variables

Backend (see backend/.env.example):

· SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
· SUPABASE_JWT_AUD, SUPABASE_STORAGE_BUCKET
· GEMINI_API_KEY, GEMINI_MODEL, EMBEDDING_MODEL
· CORS_ORIGINS

Frontend (see frontend/.env.example):

· VITE_API_URL
· VITE_SUPABASE_URL
· VITE_SUPABASE_ANON_KEY

Database Setup

Run migrations in order in the Supabase SQL Editor:

1. 001_init.sql — notes table
2. 002_documents.sql — documents, chunks (pgvector), match_chunks RPC
3. 003_quizzes_flashcards.sql — quizzes, questions, attempts, decks, cards, reviews
4. 004_progress.sql — study_events, progress_timeline RPC
5. 005_chat.sql — chat_sessions, chat_messages
6. 006_backfill_events.sql — backfill existing activity

Then create a private storage bucket named documents.

License

Personal project — not licensed for redistribution.
