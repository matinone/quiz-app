import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.main import app
from app.models.database import Base, async_engine, get_session


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
async def db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """
    Fixture to use a single DB connection for the whole testsuite.
    """
    # always drop and create test DB tables between test sessions
    async with async_engine.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()  # ensure any open transactions are committed

        yield connection


@pytest.fixture(scope="function")
async def db_session(
    db_connection: AsyncConnection
) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to create a new separate transaction for each testcase, rolling back all
    the DB changes after the test finishes.
    This ensures that each testcase starts with an empty database.
    """

    async with AsyncSession(bind=db_connection, expire_on_commit=False) as session:
        await session.begin_nested()  # create savepoint to rollback to
        yield session
        await session.rollback()  # rollback to the savepoint


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # override get_session dependency to return the DB session from the fixture
    # (instead of creating a new one)
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
