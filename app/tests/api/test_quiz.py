from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_quiz(client: AsyncClient, db_session: AsyncSession):
    quiz_data = {"title": "My quiz", "description": "My quiz description"}
    response = await client.post("/api/quiz", json=quiz_data)

    assert response.status_code == status.HTTP_201_CREATED

    response_quiz = response.json()
    for key in quiz_data:
        assert response_quiz[key] == quiz_data[key]
