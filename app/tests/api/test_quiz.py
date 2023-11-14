from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories import QuizFactory


async def test_create_quiz(client: AsyncClient, db_session: AsyncSession):
    quiz_data = {"title": "My quiz", "description": "My quiz description"}
    response = await client.post("/api/quiz", json=quiz_data)

    assert response.status_code == status.HTTP_201_CREATED

    created_quiz = response.json()
    assert "id" in created_quiz
    for key in quiz_data:
        assert created_quiz[key] == quiz_data[key]

    # created_at/updated_at should be close to the current time
    time_before = datetime.utcnow() - timedelta(minutes=2)
    time_after = datetime.utcnow() + timedelta(minutes=2)
    for key in ["created_at", "updated_at"]:
        parsed_datetime = datetime.strptime(created_quiz[key], "%Y-%m-%dT%H:%M:%S")
        assert parsed_datetime >= time_before and parsed_datetime <= time_after


@pytest.mark.parametrize("cases", ["no_quizzes", "few_quizzes", "many_quizzes"])
async def test_get_quizzes(client: AsyncClient, db_session: AsyncSession, cases: str):
    if cases == "no_quizzes":
        n_quiz = 0
    else:
        n_quiz = 3 if cases == "few_quizzes" else 30
        await QuizFactory.create_batch(n_quiz)

    response = await client.get("/api/quiz")

    assert response.status_code == status.HTTP_200_OK

    returned_quizzes = response.json()
    if cases == "no_quizzes":
        assert len(returned_quizzes) == 0
    elif cases == "few_quizzes":
        assert len(returned_quizzes) == 3
    else:
        assert len(returned_quizzes) == 25

    for quiz in returned_quizzes:
        assert "id" in quiz
        assert "title" in quiz
        assert "description" in quiz
        assert "created_at" in quiz
        assert "updated_at" in quiz


async def test_get_quizzes_query_params(client: AsyncClient, db_session: AsyncSession):
    n_quiz = 30
    await QuizFactory.create_batch(n_quiz)

    response = await client.get("/api/quiz?offset=2&limit=30")

    assert response.status_code == status.HTTP_200_OK

    returned_quizzes = response.json()
    assert len(returned_quizzes) == 28
