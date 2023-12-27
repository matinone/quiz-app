from typing import TYPE_CHECKING, Self

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base
from app.schemas import AnswerOptionCreate

if TYPE_CHECKING:
    from app.models.question import Question


class AnswerOption(Base):
    __tablename__ = "answer_options"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    content: Mapped[str] = mapped_column(String(256), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    # have to use "Question" to avoid circular dependencies
    question: Mapped["Question"] = relationship(
        "Question", back_populates="answer_options"
    )

    @classmethod
    async def create(cls, db: AsyncSession, option: AnswerOptionCreate) -> Self:
        new_option = cls(
            question_id=option.question_id,
            content=option.content,
            is_correct=option.is_correct,
        )

        db.add(new_option)
        await db.commit()
        await db.refresh(new_option)

        return new_option
