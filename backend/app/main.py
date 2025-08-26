
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from app.database import SessionLocal, init_db
from app import models, schemas
from app.config import settings
from app.llm import generate_questions
from sqlalchemy import func, text


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    pass 

app = FastAPI(title="Interview Prep Platform", version="1.0.0", lifespan=lifespan)

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

@app.post("/api/questions/generate", response_model=schemas.GenerateResponse)
def api_generate(req: schemas.GenerateRequest):
    # Additional validation (Pydantic already validates, but let's be explicit)
    if len(req.job_title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job title cannot be empty")
    if len(req.job_title) > 50:
        raise HTTPException(status_code=400, detail="Job title must be 50 characters or less")
    
    try:
        questions = generate_questions(req.job_title)
        return {"questions": questions}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate questions")


@app.post("/api/questions", response_model=schemas.QASetOut, status_code=201)
def create_set(payload: schemas.QASetCreate, db: Session = Depends(get_db)):
    # Additional validation
    if len(payload.job_title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job title cannot be empty")
    if len(payload.job_title) > 50:
        raise HTTPException(status_code=400, detail="Job title must be 50 characters or less")

    try:
        qa_set = models.QASet(job_title=payload.job_title, name=payload.name)
        db.add(qa_set)
        db.flush()  # to get set id

        for q in payload.questions:
            qtype = models.QuestionType(q.type)
            db.add(models.Question(set_id=qa_set.id, type=qtype, text=q.question))

        db.commit()
        db.refresh(qa_set)
        return qa_set
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create question set")


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
        query.order_by(models.Question.id.desc())
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
        "avg_difficulty": round(avg_diff,2) if avg_diff is not None else None,
    }


@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    # quick DB ping (portable)
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/api/questions/page", response_model=schemas.QuestionsPage, responses={404: {"model": schemas.ErrorResponse}})
def list_questions_legacy(
    set_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = list_questions(set_id=set_id, page=page, size=page_size, db=db)
    # include page_size for backward-compat
    result_dict = result if isinstance(result, dict) else result.model_dump()
    result_dict["page_size"] = result_dict.get("size")
    return result_dict
