from datetime import datetime, timedelta

import pytest
from dirty_equals import IsDatetime
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.models as models
from app.schemas import QuestionType
from app.tests.conftest import AuthInfo
from app.tests.factories.question_factory import QuestionFactory
from app.tests.factories.quiz_factory import QuizFactory


@pytest.mark.parametrize("cases", ["default", "custom"])
async def test_create_question(
    client: AsyncClient,
    db_session: AsyncSession,
    cases: str,
    auth_info: AuthInfo,
):
    # questions must be associated to an existing quiz
    quiz = await QuizFactory.create(user=auth_info.user)
    question_data = {"quiz_id": quiz.id, "content": "What is the question?"}

    if cases == "custom":
        question_data["type"] = QuestionType.multiple_choice
        question_data["points"] = 4

    response = await client.post(
        f"/api/quizzes/{quiz.id}/questions",
        json=question_data,
        headers=auth_info.headers,
    )

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


async def test_create_question_no_quiz(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_info: AuthInfo,
):
    question_data = {"content": "What is the question?"}
    response = await client.post(
        "/api/quizzes/123/questions", json=question_data, headers=auth_info.headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_question_invalid_type(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_info: AuthInfo,
):
    quiz = await QuizFactory.create(user=auth_info.user)
    question_data = {
        "quiz_id": quiz.id,
        "content": "What is the question?",
        "type": "invalid",
    }
    response = await client.post(
        f"/api/quizzes/{quiz.id}/questions",
        json=question_data,
        headers=auth_info.headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_get_questions(client: AsyncClient, db_session: AsyncSession, cases: str):
    if cases == "found":
        quiz = await QuizFactory.create()
        questions = await QuestionFactory.create_batch(5, quiz=quiz)
        quiz_id = quiz.id
    else:
        quiz_id = 123

    response = await client.get(f"/api/quizzes/{quiz_id}/questions")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK

        returned_questions = response.json()
        assert len(returned_questions) == len(questions)

        # sort questions by id so they can be iterated simultaneously
        questions = sorted(questions, key=lambda d: d.id)
        returned_questions = sorted(returned_questions, key=lambda d: d["id"])

        for created, returned in zip(questions, returned_questions):
            for key in returned:
                if key in ["created_at", "updated_at"]:
                    assert returned[key] == IsDatetime(
                        approx=getattr(created, key), delta=0, iso_string=True
                    )
                else:
                    assert returned[key] == getattr(created, key)


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_get_question(client: AsyncClient, db_session: AsyncSession, cases: str):
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
async def test_update_question(
    client: AsyncClient,
    db_session: AsyncSession,
    cases: str,
    auth_info: AuthInfo,
):
    question_id = 4
    if cases != "not_found":
        await QuestionFactory.create(
            id=question_id,
            quiz__user=auth_info.user,
            updated_at=datetime.utcnow() - timedelta(hours=5),
        )

    question_data: dict[str, str | int] = {"content": "Is this a new question?"}
    if cases != "partial_update":
        question_data["type"] = QuestionType.true_false
        question_data["points"] = 8

    if cases == "invalid":
        question_data["type"] = "invalid_type"

    before_update = datetime.utcnow() - timedelta(seconds=5)
    response = await client.put(
        f"/api/questions/{question_id}", json=question_data, headers=auth_info.headers
    )

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
    client: AsyncClient,
    db_session: AsyncSession,
    cases: str,
    auth_info: AuthInfo,
):
    question_id = 4
    if cases == "found":
        await QuestionFactory.create(id=question_id, quiz__user=auth_info.user)

    response = await client.delete(
        f"/api/questions/{question_id}", headers=auth_info.headers
    )

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # check quiz was deleted from database
        db_question = await models.Question.get(db=db_session, id=question_id)
        assert not db_question
