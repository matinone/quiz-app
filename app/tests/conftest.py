from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.main import app
from app.models.database import AsyncSessionLocal, Base, async_engine, get_session


@pytest.fixture(autouse=True)
async def db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """
    Fixture to use a single DB connection for the whole testsuite.
    """

    # always drop and create test DB tables between test sessions
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to create a new separate transaction for each testcase, rolling back all
    the DB changes after the test finishes.
    This ensures that each testcase starts with an empty database.
    """

    # async with async_engine.connect() as connection:
    #     transaction = await connection.begin()

    #     async with AsyncSessionLocal(bind=connection) as session:
    #         yield session

    #     await transaction.rollback()

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture()
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # override get_session dependency to return the DB session from the fixture
    # (instead of creating a new one)
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://0.0.0.0") as client:
        yield client
