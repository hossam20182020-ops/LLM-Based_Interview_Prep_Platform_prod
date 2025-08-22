from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class QuestionType(str, enum.Enum):
    technical = "technical"
    behavioral = "behavioral"

class QASet(Base):
    __tablename__ = "qa_sets"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(200), index=True, nullable=False)
    name = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    questions = relationship("Question", back_populates="qa_set", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("qa_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(QuestionType), nullable=False)
    text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    difficulty = Column(Float, nullable=True)  # 1.0 - 5.0
    flagged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    qa_set = relationship("QASet", back_populates="questions")
