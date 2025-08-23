from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float,
    Index, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base
import sqlalchemy as sa  # <-- add this
import enum


class QuestionType(str, enum.Enum):
    technical = "technical"
    behavioral = "behavioral"


class QASet(Base):
    __tablename__ = "qa_sets"

    id = Column(Integer, primary_key=True)  # PK is already indexed implicitly
    job_title = Column(String(200), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    questions = relationship(
        "Question",
        back_populates="qa_set",
        cascade="all, delete-orphan",
        passive_deletes=True,  # works with FK ondelete="CASCADE"
    )

    def __repr__(self) -> str:
        return f"<QASet id={self.id} job_title={self.job_title!r}>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("qa_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    # Name the Postgres enum type for cleaner Alembic diffs:
    type = Column(Enum(QuestionType, name="question_type"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    difficulty = Column(Float, nullable=True)  # 1..5 validated in API; enforced below too
    # DB-side default; avoids None when not provided (use sa.text to avoid shadowing by the 'text' column above):
    flagged = Column(Boolean, nullable=False, server_default=sa.text("false"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    qa_set = relationship("QASet", back_populates="questions")

    __table_args__ = (
        # Common pattern: filter by set_id and sort by created_at
        Index("ix_questions_set_created_at", "set_id", "created_at"),
        # Useful filter in UI
        Index("ix_questions_flagged", "flagged"),
        # Enforce difficulty range at the DB level (or allow NULL):
        CheckConstraint(
            "(difficulty IS NULL) OR (difficulty >= 1 AND difficulty <= 5)",
            name="ck_questions_difficulty_range"
        ),
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} set_id={self.set_id} type={self.type}>"