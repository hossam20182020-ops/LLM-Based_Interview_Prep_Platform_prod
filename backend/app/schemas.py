from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class QuestionCreate(BaseModel):
    type: Literal["technical", "behavioral"]
    question: str = Field(..., alias="text")

class QuestionOut(BaseModel):
    id: int
    set_id: int
    type: str
    text: str
    user_answer: Optional[str] = None
    difficulty: Optional[float] = None
    flagged: bool

    class Config:
        from_attributes = True

class QASetCreate(BaseModel):
    job_title: str
    name: Optional[str] = None
    questions: List[QuestionCreate]

class QASetOut(BaseModel):
    id: int
    job_title: str
    name: Optional[str] = None

    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    job_title: str

class GenerateResponse(BaseModel):
    questions: List[QuestionCreate]

class QuestionPatch(BaseModel):
    user_answer: Optional[str] = None
    difficulty: Optional[float] = None
    flagged: Optional[bool] = None
