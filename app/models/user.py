from datetime import datetime
from typing import TYPE_CHECKING, Self

from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database import Base
from app.schemas import UserCreate

if TYPE_CHECKING:
    from app.models.quiz import Quiz


def get_password_hash(password: str) -> str:
    return password


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, unique=True
    )
    email: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, unique=True
    )
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # have to use "Quiz" to avoid circular dependencies
    quizzes: Mapped[list["Quiz"]] = relationship("Quiz", back_populates="user")

    @classmethod
    async def create(cls, db: AsyncSession, user: UserCreate) -> Self:
        new_user = cls(
            username=user.username,
            email=user.email,
            password_hash=get_password_hash(user.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user
