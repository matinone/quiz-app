from datetime import datetime

import pytest
from dirty_equals import IsDatetime
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.models as models
from app.schemas import QuestionType
from app.tests.factories import QuizFactory


@pytest.mark.parametrize("cases", ["default", "custom"])
async def test_create_question(
    client: AsyncClient, db_session: AsyncSession, cases: str
):
    # questions must be associated to an existing quiz
    quiz = await QuizFactory.create()
    question_data = {"quiz_id": int(quiz.id), "content": "What is the question?"}

    if cases == "custom":
        question_data["type"] = QuestionType.multiple_choice
        question_data["points"] = 4

    response = await client.post("/api/question", json=question_data)

    assert response.status_code == status.HTTP_201_CREATED

    if cases == "default":
        question_data["type"] = QuestionType.open
        question_data["points"] = 1

    created_question = response.json()
    for key in question_data:
        assert created_question[key] == question_data[key]

    # created_at/updated_at should be close to the current time
    for key in ["created_at", "updated_at"]:
        assert created_question[key] == IsDatetime(
            approx=datetime.utcnow(), delta=2, iso_string=True
        )

    # check quiz exists in database
    db_question = await models.Question.get(db=db_session, id=created_question["id"])
    assert db_question
    for key in question_data:
        assert question_data[key] == getattr(db_question, key)


async def test_create_question_no_quiz(client: AsyncClient, db_session: AsyncSession):
    question_data = {"quiz_id": 10, "content": "What is the question?"}
    response = await client.post("/api/question", json=question_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_create_question_invalid_type(
    client: AsyncClient, db_session: AsyncSession
):
    quiz = await QuizFactory.create()
    question_data = {
        "quiz_id": quiz.id,
        "content": "What is the question?",
        "type": "invalid",
    }
    response = await client.post("/api/question", json=question_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
