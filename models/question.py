from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from models.database import Base
from models.quiz import Quiz
from schemas import QuestionCreate


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
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
        question = cls(
            quiz_id=QuestionCreate.quiz_id,
            content=QuestionCreate.content,
            type=QuestionCreate.type,
            points=QuestionCreate.points,
        )
        question.updated_at = func.now()
        db.add(question)
        await db.commit()
        await db.refresh(question)

        return question
