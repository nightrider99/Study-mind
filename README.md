# StudyMind AI 🧠

**Learn smarter. Practice better. Grow every day.**

An AI-powered learning assistant that helps students study smarter — upload notes, ask questions, generate quizzes and flashcards, and track progress over time.

---

## 📌 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Database Setup (Supabase)](#-database-setup-supabase)
- [Deployment](#-deployment)
- [API Overview](#-api-overview)
- [Developing on Your Phone](#-developing-on-your-phone)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 💡 About

StudyMind AI is a full-stack web application built for students. Upload your study materials (notes, PDFs), then use the app to:

- Ask questions and get answers grounded in **your own** content
- Auto-generate multiple-choice and short-answer quizzes
- Turn key concepts into flashcards for active recall
- Track quiz scores and study sessions over time

The project is designed as a monorepo: a **React + TypeScript** frontend and a **Python FastAPI** backend, deployed independently (Vercel + Render) from a single GitHub repository.

---

## ✨ Features

### 📚 AI Notes & PDF Assistant
- Upload study notes and PDF documents
- Ask questions about uploaded materials
- Get answers based on the provided content, with references to relevant sections where possible

### 📝 Quiz Generator
- Generate multiple-choice questions from study materials
- Create short-answer practice questions
- Take quizzes and receive instant scores
- Review correct answers with explanations

### 🗂️ Smart Flashcards
- Automatically turn important concepts into Q&A flashcards
- Review flashcards for active recall and spaced revision

### 📊 Learning Progress Dashboard
- Track quiz scores and performance over time
- Record completed study sessions
- Identify topics that need more practice

> **Note:** AI-powered features (Q&A, quiz generation, flashcard extraction) are planned and will be layered on top of the core app.

---

## 🛠️ Tech Stack

| Layer      | Technology                          | Hosted On        |
|------------|-------------------------------------|------------------|
| Frontend   | React 18 + TypeScript + Vite        | Vercel           |
| Styling    | Tailwind CSS                        | —                |
| Backend    | Python 3.10+ + FastAPI              | Render           |
| Database   | PostgreSQL (via Supabase)           | Supabase (free)  |
| File Storage | Supabase Storage (PDF uploads)    | Supabase (free)  |
| PDF Parsing | pypdf                              | —                |
| AI (planned) | LLM API integration               | TBD              |

---

## 🏗️ Architecture
Here's your complete `README.md` — copy this into the root of your repo (you can paste it directly in the GitHub mobile app or web editor):

```markdown
# StudyMind AI 🧠

**Learn smarter. Practice better. Grow every day.**

An AI-powered learning assistant that helps students study smarter — upload notes, ask questions, generate quizzes and flashcards, and track progress over time.

---

## 📌 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Database Setup (Supabase)](#-database-setup-supabase)
- [Deployment](#-deployment)
- [API Overview](#-api-overview)
- [Developing on Your Phone](#-developing-on-your-phone)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 💡 About

StudyMind AI is a full-stack web application built for students. Upload your study materials (notes, PDFs), then use the app to:

- Ask questions and get answers grounded in **your own** content
- Auto-generate multiple-choice and short-answer quizzes
- Turn key concepts into flashcards for active recall
- Track quiz scores and study sessions over time

The project is designed as a monorepo: a **React + TypeScript** frontend and a **Python FastAPI** backend, deployed independently (Vercel + Render) from a single GitHub repository.

---

## ✨ Features

### 📚 AI Notes & PDF Assistant
- Upload study notes and PDF documents
- Ask questions about uploaded materials
- Get answers based on the provided content, with references to relevant sections where possible

### 📝 Quiz Generator
- Generate multiple-choice questions from study materials
- Create short-answer practice questions
- Take quizzes and receive instant scores
- Review correct answers with explanations

### 🗂️ Smart Flashcards
- Automatically turn important concepts into Q&A flashcards
- Review flashcards for active recall and spaced revision

### 📊 Learning Progress Dashboard
- Track quiz scores and performance over time
- Record completed study sessions
- Identify topics that need more practice

> **Note:** AI-powered features (Q&A, quiz generation, flashcard extraction) are planned and will be layered on top of the core app.

---

## 🛠️ Tech Stack

| Layer      | Technology                          | Hosted On        |
|------------|-------------------------------------|------------------|
| Frontend   | React 18 + TypeScript + Vite        | Vercel           |
| Styling    | Tailwind CSS                        | —                |
| Backend    | Python 3.10+ + FastAPI              | Render           |
| Database   | PostgreSQL (via Supabase)           | Supabase (free)  |
| File Storage | Supabase Storage (PDF uploads)    | Supabase (free)  |
| PDF Parsing | pypdf                              | —                |
| AI (planned) | LLM API integration               | TBD              |

---

## 🏗️ Architecture

```

┌──────────────────┐         HTTPS / JSON          ┌────────────────────┐
│                  │   ──────────────────────────► │                    │
│   React + TS     │                               │   FastAPI (Render) │
│   Frontend       │   ◄────────────────────────── │                    │
│   (Vercel)       │                               └─────────┬──────────┘
└──────────────────┘                                         │
┌──────────────┴───────────────┐
│                              │
┌──────▼───────┐            ┌─────────▼────────┐
│  PostgreSQL  │            │ Supabase Storage │
│  (tables:    │            │ (uploaded PDFs)  │
│  documents,  │            │                  │
│  quizzes,    │            │                  │
│  flashcards, │            │                  │
│  sessions)   │            │                  │
└──────────────┘            └──────────────────┘

```

**Why this architecture?**

- **Monorepo** — one GitHub repo, but frontend and backend deploy independently
- **Vercel** — zero-config React/Vite hosting with preview deployments on every PR
- **Render** — simple Python web service hosting with auto-deploy from GitHub
- **Supabase** — free managed Postgres **and** file storage in one place; Render's free disk is ephemeral (wiped on redeploy), so files and data must live externally

---

## 📁 Project Structure

```

study-mind/
├── frontend/                    # React + TypeScript app → deployed to Vercel
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx    # Learning progress dashboard
│   │   │   ├── Upload.tsx       # Notes/PDF upload page
│   │   │   ├── Quiz.tsx         # Quiz taking & review
│   │   │   └── Flashcards.tsx   # Flashcard review
│   │   ├── lib/
│   │   │   └── api.ts           # All backend API calls (single source of truth)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env                     # Local secrets — NOT committed
│   ├── .env.example             # Template for required env vars
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── package.json
│
├── backend/                     # FastAPI app → deployed to Render
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # App entry point + CORS config
│   │   ├── database.py          # Supabase client setup
│   │   ├── models.py            # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── documents.py     # Upload & notes endpoints
│   │   │   ├── quizzes.py       # Quiz generation & scoring
│   │   │   ├── flashcards.py    # Flashcard endpoints
│   │   │   └── progress.py      # Scores & study sessions
│   ├── .env                     # Local secrets — NOT committed
│   ├── .env.example
│   ├── requirements.txt
│   └── render.yaml              # Render deployment config
│
├── .gitignore                   # Ignores .env files, node_modules, .venv
└── README.md

```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Git | any | — |
| Node.js + npm | 18+ | Frontend only |
| Python | 3.10+ | Backend only |

> **No computer?** See [Developing on Your Phone](#-developing-on-your-phone) — this project can be built entirely from a phone using cloud tools.

### 1. Clone the repository

```bash
git clone https://github.com/nightrider99/study-mind.git
cd study-mind
```

### 2. Set up the database

Follow [Database Setup](#-database-setup-supabase) first — you need the `SUPABASE_URL` and `SUPABASE_KEY` before the backend will run.

### 3. Backend setup

```bash
cd backend
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env` (see [Environment Variables](#-environment-variables)), then start the server:

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`.
Interactive API docs (auto-generated by FastAPI): **http://localhost:8000/docs**

### 4. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app is now running at **http://localhost:5173**

---

## 🔐 Environment Variables

### Backend — `backend/.env` (never commit this file)

| Variable | Description | Where to get it |
| --- | --- | --- |
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | `anon` / `public` key | Supabase Dashboard → Settings → API |

Copy `backend/.env.example` → `backend/.env` and fill in the values.

### Frontend — `frontend/.env` (never commit this file)

| Variable | Description | Example |
| --- | --- | --- |
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` (local) or `https://your-api.onrender.com` (production) |

Copy `frontend/.env.example` → `frontend/.env` and fill in the value.

> **Security note:** The Supabase `anon` key is safe to use from the backend (it's designed for client-side use with Row Level Security). Never commit either `.env` file — both are covered by `.gitignore`.

---

## 🗄️ Database Setup (Supabase)

We use [Supabase](https://supabase.com) — free tier includes **500 MB Postgres** and **1 GB file storage**.

1. Sign up at [supabase.com](https://supabase.com) (GitHub login works)
2. **New Project** → choose a name and database password → select a region close to your Render region
3. Wait for the project to provision (2 minutes)
4. Go to **Project Settings → API** and copy:
   - `Project URL` → your `SUPABASE_URL`
   - `anon public` key → your `SUPABASE_KEY`
5. Go to the **SQL Editor** and create your first table:

```sql
create table documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  file_path text,              -- path in Supabase Storage
  extracted_text text,
  created_at timestamptz default now()
);

create table quizzes (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade,
  questions jsonb not null,    -- [{question, options, answer, explanation}]
  score int,
  created_at timestamptz default now()
);

create table flashcards (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade,
  front text not null,
  back text not null,
  created_at timestamptz default now()
);

create table study_sessions (
  id uuid primary key default gen_random_uuid(),
  duration_minutes int not null,
  activity text,               -- e.g. 'quiz', 'flashcards', 'reading'
  created_at timestamptz default now()
);
```

6. For PDF uploads: go to **Storage → New Bucket**, name it `documents`, and set it to **private** (files are served through your backend, not publicly).

---

## 🌐 Deployment

Both services auto-deploy from the same GitHub repo. Push to `main` → both redeploy.

### Backend → Render

1. Push your code to GitHub
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Web Service** → connect your repo
3. Render auto-detects `backend/render.yaml`, or configure manually:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment**, add:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon key
5. **Deploy** — then verify `https://your-api.onrender.com/api/health` returns `{"status": "ok"}` and explore `/docs`

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New → Project** → import your repo
2. Configure:
   - **Root Directory:** `frontend` (click "Edit" to change it)
   - **Framework Preset:** Vite (auto-detected)
3. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://your-api.onrender.com`
4. **Deploy** — Vercel gives you a URL like `https://your-app.vercel.app`

### Final wiring step ⚠️

After deploying the frontend, update CORS in `backend/app/main.py` with your real Vercel URL and push:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app",   # ← your actual Vercel URL
],
```

### ⚠️ Render free tier notes

- Services **sleep after ~15 minutes** of inactivity; the first request after sleep takes 50 seconds (cold start). This is normal.
- Render's filesystem is **ephemeral** — never store uploads or SQLite files there. Everything persists in Supabase.

---

## 📡 API Overview

Base URL: `http://localhost:8000` (dev) / `https://your-api.onrender.com` (prod)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/documents/` | Upload a document (PDF/notes) |
| GET | `/api/documents/` | List all uploaded documents |
| GET | `/api/documents/{id}` | Get one document (with extracted text) |
| DELETE | `/api/documents/{id}` | Delete a document |
| POST | `/api/documents/{id}/ask` | Ask a question about a document *(planned)* |
| POST | `/api/quizzes/generate` | Generate a quiz from a document *(planned)* |
| POST | `/api/quizzes/{id}/submit` | Submit quiz answers, get score |
| GET | `/api/quizzes/` | List past quizzes |
| GET | `/api/flashcards/` | List flashcards |
| POST | `/api/flashcards/generate` | Generate flashcards from a document *(planned)* |
| GET | `/api/progress/` | Dashboard stats (scores, sessions) |

Interactive docs available at `/docs` on any running backend instance — great for testing from a phone browser.

---

## 📱 Developing on Your Phone

This project can be built and deployed entirely from a phone:

| Tool | Best for | Platform |
| --- | --- | --- |
| **GitHub mobile app** | Commits, PRs, editing small files | iOS + Android |
| **GitHub Codespaces** | Full VS Code + terminal in browser (free monthly hours) | iOS + Android |
| **Supabase web dashboard** | SQL Editor, table management, storage — mobile-friendly | iOS + Android |
| **Render / Vercel dashboards** | Deployments, logs, env vars | iOS + Android |
| **Termux + Acode** | Local terminal + code editor (git, python, node) | Android only |
| **FastAPI `/docs`** | Testing the whole backend from a browser | iOS + Android |

**Recommended workflow:** GitHub app for small edits → Codespaces for real coding sessions → Render & Vercel dashboards for deploys and logs. A Bluetooth keyboard helps a lot with Codespaces.

---

## 🗺️ Roadmap

- Define architecture (Vercel + Render + Supabase)
- Monorepo structure with separate `frontend/` and `backend/`
- Set up the React + TypeScript frontend
- Set up the FastAPI backend
- Set up Supabase database and storage
- Build the study dashboard UI
- Add PDF and notes upload functionality
- Implement document text extraction (pypdf)
- Add AI-powered question answering
- Build the quiz generator
- Add smart flashcards
- Track quiz scores and study sessions
- Add topic-based progress tracking
- Improve usability and mobile responsiveness

---

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🩺 Troubleshooting

| Symptom | Fix |
| --- | --- |
| Frontend shows "Network Error" / CORS errors | Add your exact Vercel URL to `allow_origins` in `backend/app/main.py` and redeploy |
| First API request is very slow | Render free tier cold start — normal, subsequent requests are fast |
| Uploads disappear after redeploy | Files must go to Supabase Storage, never Render's local disk |
| `ModuleNotFoundError` on Render | Missing package → add it to `backend/requirements.txt` and push |
| Env vars not working | Vercel needs `VITE_` prefix for frontend vars; Render vars need a redeploy to take effect |
| Database connection fails | Check `SUPABASE_URL`/`SUPABASE_KEY` in Render → Environment; make sure you're using the `anon` key |

---

## 📄 License

This project is currently under development. A license will be added when one is selected.

---

**StudyMind AI** — Learn smarter. Practice better. Grow every day.

```

## A few things I deliberately changed from your old README

1. **Prerequisites removed "phone-only" phrasing** and moved that to a dedicated section — your old README assumed a desktop terminal, which doesn't match your situation.
2. **Added the troubleshooting table** — on a phone you can't easily debug, so having the 6 most likely failures documented matters.
3. **Added a SQL starter schema** — you can paste it straight into the Supabase SQL Editor from your phone and have working tables in 2 minutes.
4. **Marked the first two roadmap items as done** since we've now defined the architecture and structure.

Next natural step: the `backend/` starter code — `main.py`, `database.py`, and `requirements.txt` so your Render deploy works on the first push. Want that?
