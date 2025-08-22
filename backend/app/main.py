from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal, init_db
import models, schemas
from config import settings
from llm import generate_questions
from sqlalchemy import func, text

app = FastAPI(title="Interview Prep Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/questions/generate", response_model=schemas.GenerateResponse)
def api_generate(req: schemas.GenerateRequest):
    questions = generate_questions(req.job_title)
    return {"questions": questions}


@app.post("/api/questions", response_model=schemas.QASetOut, status_code=201)
def create_set(payload: schemas.QASetCreate, db: Session = Depends(get_db)):
    qa_set = models.QASet(job_title=payload.job_title, name=payload.name)
    db.add(qa_set)
    db.flush()  # to get set id

    for q in payload.questions:
        qtype = models.QuestionType(q.type)
        db.add(models.Question(set_id=qa_set.id, type=qtype, text=q.question))

    db.commit()
    db.refresh(qa_set)
    return qa_set


@app.get(
    "/api/questions",
    response_model=schemas.QuestionsPage,
    responses={400: {"model": schemas.ErrorResponse}},
)
def list_questions(
    set_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Paginated list of questions with optional set_id filter.
    Returns: { items, total, page, size, pages }
    """
    query = db.query(models.Question)
    if set_id is not None:
        query = query.filter(models.Question.set_id == set_id)
    total = query.count()
    pages = (total + size - 1) // size  # Calculate total pages
    rows = (
        query.order_by(models.Question.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [schemas.QuestionOut.model_validate(r) for r in rows]
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}


@app.delete("/api/questions/{qid}", responses={404: {"model": schemas.ErrorResponse}})
def delete_question(qid: int, db: Session = Depends(get_db)):
    q = db.get(models.Question, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"ok": True}


@app.patch(
    "/api/questions/{qid}",
    response_model=schemas.QuestionOut,
    responses={404: {"model": schemas.ErrorResponse}, 400: {"model": schemas.ErrorResponse}},
)
def update_question(qid: int, payload: schemas.QuestionPatch, db: Session = Depends(get_db)):
    q = db.get(models.Question, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    if payload.user_answer is not None:
        q.user_answer = payload.user_answer

    if payload.difficulty is not None:
        if not (1.0 <= payload.difficulty <= 5.0):
            raise HTTPException(status_code=400, detail="Difficulty must be between 1 and 5")
        q.difficulty = payload.difficulty

    if payload.flagged is not None:
        q.flagged = payload.flagged

    db.commit()
    db.refresh(q)
    return q


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    total_sets = db.query(models.QASet).count()
    total_questions = db.query(models.Question).count()
    flagged = db.query(models.Question).filter(models.Question.flagged.is_(True)).count()
    avg_diff = db.query(func.avg(models.Question.difficulty)).scalar()
    return {
        "total_sets": total_sets,
        "total_questions": total_questions,
        "flagged_questions": flagged,
        "avg_difficulty": float(avg_diff) if avg_diff is not None else None,
    }


@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    # quick DB ping (portable)
    db.execute(text("SELECT 1"))
    return {"status": "ok"}