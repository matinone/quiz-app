from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.models as models
from app.schemas import QuestionType
from app.tests.factories.question_factory import QuestionFactory


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_get_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    question_id = 4
    if cases == "found":
        created_question = await QuestionFactory.create(id=question_id)

    response = await client.get(f"/api/questions/{question_id}")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK

        question = response.json()
        for key in ["id", "quiz_id", "content", "type", "points"]:
            assert question[key] == getattr(created_question, key)
        for key in ["created_at", "updated_at"]:
            assert question[key] == getattr(created_question, key).isoformat()


@pytest.mark.parametrize("cases", ["found", "not_found", "partial_update", "invalid"])
async def test_update_quiz(client: AsyncClient, db_session: AsyncSession, cases: str):
    question_id = 4
    if cases != "not_found":
        await QuestionFactory.create(
            id=question_id, updated_at=datetime.utcnow() - timedelta(hours=5)
        )

    question_data: dict[str, str | int] = {"content": "Is this a new question?"}
    if cases != "partial_update":
        question_data["type"] = QuestionType.true_false
        question_data["points"] = 8

    if cases == "invalid":
        question_data["type"] = "invalid_type"

    before_update = datetime.utcnow() - timedelta(seconds=5)
    response = await client.put(f"/api/questions/{question_id}", json=question_data)

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    elif cases == "invalid":
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        assert response.status_code == status.HTTP_200_OK

        # check response and database
        updated_quiz = response.json()
        db_question = await models.Question.get(db=db_session, id=question_id)

        assert db_question
        assert updated_quiz["id"] == question_id
        modified_keys = ["content"]
        if cases != "partial_update":
            modified_keys.append("type")
            modified_keys.append("points")

        for key in modified_keys:
            assert updated_quiz[key] == question_data[key]
            assert getattr(db_question, key) == question_data[key]

        # check updated_at column is updated
        assert db_question.updated_at >= before_update


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_delete_question(
    client: AsyncClient, db_session: AsyncSession, cases: str
):
    question_id = 4
    if cases == "found":
        await QuestionFactory.create(id=question_id)

    response = await client.delete(f"/api/questions/{question_id}")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # check quiz was deleted from database
        db_question = await models.Question.get(db=db_session, id=question_id)
        assert not db_question
