from datetime import datetime
from typing import TYPE_CHECKING, Self

from sqlalchemy import DateTime, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.security import get_password_hash
from app.models.database import Base
from app.schemas import UserCreate

if TYPE_CHECKING:
    from app.models.quiz import Quiz


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

    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str) -> Self | None:
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar()

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Self | None:
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar()
