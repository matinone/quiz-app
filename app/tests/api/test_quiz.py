from datetime import datetime, timedelta

import pytest
from dirty_equals import IsDatetime, IsInt, IsNonNegative, IsNow, IsStr
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.models as models
from app.tests.factories import QuizFactory


# add test with missing title/description
@pytest.mark.parametrize("cases", ["full", "no_title", "no_description"])
async def test_create_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    quiz_data = {"title": "My quiz", "description": "My quiz description"}
    if cases == "no_title":
        quiz_data.pop("title")
    elif cases == "no_description":
        quiz_data.pop("description")

    response = await client.post("/api/quiz", json=quiz_data)

    if cases == "no_title":
        assert response.status_code == status.HTTP_422_UNPROCESSABLEs_ENTITY
    else:
        assert response.status_code == status.HTTP_201_CREATED

        created_quiz = response.json()
        assert "id" in created_quiz
        for key in quiz_data:
            assert created_quiz[key] == quiz_data[key]

        # created_at/updated_at should be close to the current time
        for key in ["created_at", "updated_at"]:
            assert created_quiz[key] == IsDatetime(
                approx=datetime.utcnow(), delta=5, iso_string=True
            )

        # check quiz exists in database
        db_quiz = await models.Quiz.get(db=db_session, id=created_quiz["id"])
        assert db_quiz
        for key in quiz_data:
            assert quiz_data[key] == getattr(db_quiz, key)


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
        assert quiz == {
            "id": IsInt & IsNonNegative,
            "title": IsStr,
            "description": IsStr,
            "created_at": IsNow(iso_string=True),
            "updated_at": IsNow(iso_string=True),
        }


async def test_get_quizzes_query_params(client: AsyncClient, db_session: AsyncSession):
    n_quiz = 30
    await QuizFactory.create_batch(n_quiz)

    response = await client.get("/api/quiz?offset=2&limit=30")

    assert response.status_code == status.HTTP_200_OK

    returned_quizzes = response.json()
    assert len(returned_quizzes) == 28


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_get_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    quiz_id = 4
    if cases == "found":
        created_quiz = await QuizFactory.create(id=quiz_id)

    response = await client.get(f"/api/quiz/{quiz_id}")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK

        quiz = response.json()
        for key in ["id", "title", "description"]:
            assert quiz[key] == getattr(created_quiz, key)
        for key in ["created_at", "updated_at"]:
            assert quiz[key] == getattr(created_quiz, key).isoformat()


@pytest.mark.parametrize("cases", ["found", "not_found", "partial_update"])
async def test_update_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    quiz_id = 4
    if cases != "not_found":
        await QuizFactory.create(
            id=quiz_id, updated_at=datetime.utcnow() - timedelta(hours=5)
        )

    quiz_data = {"title": "New title"}
    if cases != "partial_update":
        quiz_data["description"] = "New description"

    before_update = datetime.utcnow() - timedelta(seconds=5)
    response = await client.put(f"/api/quiz/{quiz_id}", json=quiz_data)

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK

        # check response and database
        updated_quiz = response.json()
        db_quiz = await models.Quiz.get(db=db_session, id=quiz_id)

        assert db_quiz
        assert updated_quiz["id"] == quiz_id
        modified_keys = ["title"]
        if cases != "partial_update":
            modified_keys.append("description")

        for key in modified_keys:
            assert updated_quiz[key] == quiz_data[key]
            assert getattr(db_quiz, key) == quiz_data[key]

        # check updated_at column is updated
        assert db_quiz.updated_at >= before_update


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_delete_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    quiz_id = 4
    if cases == "found":
        await QuizFactory.create(id=quiz_id)

    response = await client.delete(f"/api/quiz/{quiz_id}")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # check quiz was deleted from database
        db_quiz = await models.Quiz.get(db=db_session, id=quiz_id)
        assert not db_quiz
