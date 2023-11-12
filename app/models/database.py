from typing import Annotated, Any, AsyncGenerator, Self

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.settings import get_settings


class Base(DeclarativeBase):
    """
    This Base class also defines common methods for CRUD operations.
    """

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> Self | None:
        result = await db.execute(select(cls).where(cls.id == id))
        return result.scalar()

    @classmethod
    async def update(
        cls, db: AsyncSession, current: Self, new: BaseModel | dict[str, Any]
    ) -> Self:
        if isinstance(new, dict):
            update_data = new
        else:
            # exclude_unset=True to avoid updating to default values
            update_data = new.dict(exclude_unset=True)

        current_data = jsonable_encoder(current)
        for field in current_data:
            if field in update_data:
                setattr(current, field, update_data[field])

        if hasattr(current, "updated_at"):
            current.updated_at = func.now()

        db.add(current)
        await db.commit()
        await db.refresh(current)

        return current

    @classmethod
    async def delete(cls, db: AsyncSession, db_obj) -> Self:
        await db.delete(db_obj)
        await db.commit()

        return db_obj

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: int) -> Self | None:
        db_obj = await cls.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

        return db_obj


settings = get_settings()
async_engine = create_async_engine(
    settings.DB_URL, pool_pre_ping=True, echo=settings.ECHO_SQL
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, future=True)


async def init_db():
    if not settings.USE_ALEMBIC:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to create/close a new session per request, making sure that the session
    is always closed even if there is an error (thanks to the async context manager).
    """
    async with AsyncSessionLocal() as session:
        yield session


# type alias for the database session
AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
