# StudyMind AI

A small, working static study app with an optional FastAPI + Gemini question-answering backend.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
# Add GEMINI_API_KEY to .env for AI answers
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`, health check at `/api/health`, and docs at `/docs`.

### Frontend

Serve the repository root with a static server rather than opening files directly:

```bash
python -m http.server 5500
```

Open `http://localhost:5500`. Notes and quizzes work without the backend; the Ask AI box uses `http://localhost:8000` by default.

## Deploy

1. Deploy `backend/` to Render using the included `render.yaml`.
2. Add `GEMINI_API_KEY` in Render's environment settings.
3. Edit `api-config.js` and replace the local URL with your Render URL, then push.
4. Host the repository root on GitHub Pages. Add the exact Pages origin to `FRONTEND_ORIGINS` if it differs from the default.

Never commit `.env` or a Gemini API key.
