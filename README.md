# LLM-Based Interview Prep Platform

A full-stack app to generate, save, and organize interview questions, rate their difficulty, and flag interesting ones.

## Stack
- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL
- **Frontend:** React (Vite)
- **AI:** Gemini (Google AI Studio)
- **Containerization:** Docker Compose

## Quick Start (Beginner Friendly)

1. **Install** Docker Desktop (or Docker Engine) and make sure `docker compose` works.
2. **Copy env file:**  
   ```bash
   cp .env.example .env
   ```
   - Put your actual Gemini API key into `GEMINI_API_KEY=` (or leave blank to use a simple fallback generator).
3. **Run the stack:**  
   ```bash
   docker compose up --build
   ```
4. **Open the app:**  
   - Frontend: http://localhost:3000  
   - Backend docs: http://localhost:8000/docs

> If you see CORS errors, ensure `CORS_ORIGINS` in the backend container includes `http://localhost:3000`.

## How It Works

- Use the **Generate** form to ask the LLM for questions (technical + behavioral) for a chosen job title.
- **Save as Set** to persist the generated questions to the database.
- On the Saved Questions list:
  - **Rate difficulty** (1–5).
  - **Flag** interesting questions.
- **Stats** shows totals and averages.

## API Overview

- `POST /api/questions/generate` — body: `{ "job_title": "Backend Developer" }`  
  returns: `{ "questions": [{ "type": "technical|behavioral", "text": "..." }, ...] }`
- `POST /api/questions` — body: `{ "job_title": "...", "name": "optional", "questions": [...] }`
- `GET /api/questions?set_id=<id>` — list questions (optionally filter by set)
- `PATCH /api/questions/{id}` — update difficulty/flag/answer
- `DELETE /api/questions/{id}` — remove a question
- `GET /api/stats` — simple global metrics

## Data Model

- `qa_sets(id, job_title, name, created_at)`
- `questions(id, set_id -> qa_sets.id, type, text, user_answer, difficulty, flagged, created_at)`

## Local Dev (Outside Docker)

- Backend:
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  export DATABASE_URL=postgresql+psycopg2://interview:interview_pw@localhost:5432/interview_prep
  export GEMINI_API_KEY=your_key
  uvicorn app.main:app --reload
  ```

- Frontend:
  ```bash
  cd frontend
  npm i
  npm run dev
  ```

## Notes

- If you don't provide a `GEMINI_API_KEY`, the app uses a basic fallback that returns a fixed set of reasonable questions.
- Postgres data persists to a Docker volume named `pgdata`.
- You can extend this with user accounts, pagination, and better set browsing.

---

## Performance & Bonus Additions

### Pagination
New endpoint: `GET /api/questions/page?page=1&page_size=10&set_id=<optional>`  
Returns:
```json
{
  "items": [ /* QuestionOut[] */ ],
  "page": 1,
  "page_size": 10,
  "total": 123,
  "pages": 13
}
```
The frontend `QuestionList` uses this with **Prev/Next** controls and a **Page size** selector.

### Async loading indicators
Already implemented in React: "Generating..." for LLM calls, "Loading..." for lists.

### Responsive UI
Basic responsive layout via `src/styles.css`, adaptive grid on ≥720px, card components, and mobile-friendly spacing.

### Unit Tests
- **Backend:** `pytest` tests under `backend/tests/` using in-memory SQLite and FastAPI `TestClient`.
- **Frontend:** minimal Vitest test `App.test.tsx`.

### CI/CD
GitHub Actions workflow at `.github/workflows/ci.yml` runs backend tests + frontend build/tests on each push/PR.

