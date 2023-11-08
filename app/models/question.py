from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database import Base
from app.models.quiz import Quiz
from app.schemas import QuestionCreate


class Question(Base):
    __tablename__ = "questions"

    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizes.id"))
    content: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    points: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    quiz: Mapped[Quiz] = relationship("Quiz", back_populates="questions")

    @classmethod
    async def create(cls, db: AsyncSession, question: QuestionCreate) -> Self:
        new_question = cls(
            quiz_id=QuestionCreate.quiz_id,
            content=QuestionCreate.content,
            type=QuestionCreate.type,
            points=QuestionCreate.points,
        )
        new_question.updated_at = func.now()
        db.add(new_question)
        await db.commit()
        await db.refresh(new_question)

        return new_question
