from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database import Base
from app.models.question import Question
from app.schemas import QuizCreate


class Quiz(Base):
    __tablename__ = "quizzes"

    title: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # TODO: add created_by column once users table is available

    questions: Mapped[list[Question]] = relationship(
        "Question", back_populates="quiz", cascade="delete, delete-orphan"
    )

    @classmethod
    async def create(cls, db: AsyncSession, quiz: QuizCreate) -> Self:
        new_quiz = cls(title=QuizCreate.title, description=QuizCreate.description)
        new_quiz.updated_at = func.now()
        db.add(new_quiz)
        await db.commit()
        await db.refresh(new_quiz)

        return new_quiz
