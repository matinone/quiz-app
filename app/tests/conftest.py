import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, SessionTransaction
from sqlalchemy.sql import text

from app.main import app
from app.models.database import AsyncSessionLocal, Base, async_engine, get_session
from app.tests.factories import factory_list


@pytest.fixture(scope="session")
def event_loop():
    """
    Custom session-scoped event loop fixture, created to be able to use the
    db_connection fixture with a session scope.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def db_connection() -> None:
    """
    Fixture to create database tables from scratch for each test session.
    """
    # always drop and create test DB tables between test sessions
    async with async_engine.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_engine.connect() as conn:
        await conn.begin()
        # enforce foreign key contraints (PRAGMA foreign_keys applies to a connection)
        await conn.execute(text("PRAGMA foreign_keys = 1"))
        await conn.begin_nested()
        async_session = AsyncSessionLocal(bind=conn, expire_on_commit=False)

        # ensures a savepoint is always available to roll back to
        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session: Session, transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        for factory in factory_list:
            factory._meta.sqlalchemy_session = async_session

        yield async_session
        await async_session.close()
        await conn.rollback()

    await async_engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # override get_session dependency to return the DB session from the fixture
    # (instead of creating a new one)
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
