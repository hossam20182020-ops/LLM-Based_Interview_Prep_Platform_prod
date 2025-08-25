# LLM-Based Interview Prep Platform

## 📌 Short Project Summary
A full-stack app to generate, save, and organize interview questions, rate their difficulty, and flag interesting ones.  
Built with **FastAPI (backend)**, **React (frontend)**, **PostgreSQL (database)**, and **Docker Compose**, with **Gemini (Google AI Studio)** powering AI question generation.  
Includes **pagination, stats, async loading indicators, responsive design, and CI**.

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop (or Docker Engine with `docker compose`)
- Python 3.11+
- Node.js 20+
- PostgreSQL (or use the included container)

### Quick Start (Beginner Friendly)
1. **Install** Docker Desktop and confirm `docker compose` works.  
2. **Copy env file:**
   ```bash
   cp .env.example .env
   ```
   - Put your Gemini API key into `GEMINI_API_KEY=`.
   - If left blank, the app uses a **basic fallback** that returns a fixed set of questions.
3. **Run the stack:**
   ```bash
   docker compose up --build
   ```
4. **Open the app:**
   - Frontend: [http://localhost:3001](http://localhost:3001)  
   - Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

👉 If you see **CORS errors**, ensure `CORS_ORIGINS` in backend includes `http://localhost:3001`.

### Local Dev (Outside Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://interview:interview_pw@localhost:5432/interview_prep
export GEMINI_API_KEY=your_key
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## ▶️ How to Run It
- **Local (Docker):**  
  ```bash
  docker compose up --build
  ```
- **Local (Manual):** Run backend + frontend separately.  
---

## 📡 API Routes and Usage

### Health
- `GET /healthz` → Service health

### Questions
- `POST /api/questions/generate`  
  **Body:** `{ "job_title": "Backend Developer" }`  
  **Returns:** `[{ "type": "technical|behavioral", "text": "..." }]`

- `POST /api/questions` → Save generated questions.  
- `GET /api/questions?set_id=<id>` → List questions (optionally filter by set).  
- `PATCH /api/questions/{id}` → Update difficulty / flag / user answer.  
- `DELETE /api/questions/{id}` → Delete a question.  
- `GET /api/stats` → Global metrics.  

### Pagination
- `GET /api/questions/page?page=1&page_size=10&set_id=<optional>`  
  **Returns:**
  ```json
  {
    "items": [ /* QuestionOut[] */ ],
    "page": 1,
    "page_size": 10,
    "total": 123,
    "pages": 13
  }
  ```

---

## 🖥️ Frontend + Backend Overview

### Frontend (React + Vite + Tailwind)
- Pages: **Generate, Saved Questions, Stats**
- Uses `api.ts` for typed API calls
- Responsive layout (CSS grid + Tailwind)
- Async loading indicators (“Generating…”, “Loading…”)

### Backend (FastAPI + SQLAlchemy + Alembic)
- REST API with **Pydantic models**
- **Alembic migrations** (runs on container start)
- PostgreSQL ORM layer with SQLAlchemy
- CI via **GitHub Actions** (`.github/workflows/ci.yml`)

---

## 🗄️ Data Schema

### Tables
- **qa_sets** → `(id, job_title, name, created_at)`
- **questions** → `(id, set_id → qa_sets.id, type, text, user_answer, difficulty, flagged, created_at)`

### Features
- Questions can be **rated** (difficulty 1–5)  
- Questions can be **flagged**  
- Stats show **totals and averages**

---

## 🤖 Gemini Studio Integration
- Integration via `google-generativeai` SDK
- Model: **gemini-1.5-flash** (default)
- Configured with `.env → GEMINI_API_KEY`
- Generates **technical + behavioral questions** based on job title

---

## ⚠️ Limitations / Known Issues
- No authentication/authorization (all endpoints public)  
- No rate limiting yet  
- AI output can vary in quality/consistency  
- Currently optimized for **English only**  

---

## 🛠️ Production Notes
- Always create `.env` from `.env.example` and **never commit secrets**  
- Backend CORS defaults to `http://localhost:3001` (configurable)  
- Postgres data persists to a Docker volume `pgdata`  
- Frontend is served by nginx with SPA fallback  

---

## ✅ Extra Features
- **Unit Tests:**  
  - Backend: `pytest` with SQLite + FastAPI TestClient.  
  - Frontend: minimal Vitest test `App.test.tsx`.  
- **CI:** GitHub Actions CI runs backend tests + frontend build/tests on push/PR.  
- **Responsive UI:** Works across desktop and mobile.  
- **Extensibility:** Easy to add auth, pagination improvements, user accounts.  
