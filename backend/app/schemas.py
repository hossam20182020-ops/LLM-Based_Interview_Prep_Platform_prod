from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal


# ---------- Questions ----------
class QuestionCreate(BaseModel):
    # Accept either {"text": "..."} (alias) or {"question": "..."} (field name)
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["technical", "behavioral"]
    question: str = Field(..., alias="text")


class QuestionOut(BaseModel):
    # ORM mode so model_validate() works with SQLAlchemy rows
    model_config = ConfigDict(from_attributes=True)
    id: int
    set_id: int
    type: str
    text: str
    user_answer: Optional[str] = None
    difficulty: Optional[float] = Field(None, ge=1, le=5)
    flagged: bool = False


class QuestionPatch(BaseModel):
    user_answer: Optional[str] = None
    difficulty: Optional[float] = Field(None, ge=1, le=5)
    flagged: Optional[bool] = None


# ---------- Sets ----------
class QASetCreate(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=50, description="Job title (max 50 characters)")
    name: Optional[str] = None
    questions: List[QuestionCreate]


class QASetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_title: str = Field(..., min_length=1, max_length=50, description="Job title (max 50 characters)")
    name: Optional[str] = None


# ---------- Generation ----------
class GenerateRequest(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=50, description="Job title (max 50 characters)")


class GenerateResponse(BaseModel):
    questions: List[QuestionCreate]


# ---------- Pagination & Errors ----------
class QuestionsPage(BaseModel):
    items: List[QuestionOut]
    total: int
    page: int
    size: int
    pages: int  # Add this field for frontend compatibility


class ErrorResponse(BaseModel):
    detail: str