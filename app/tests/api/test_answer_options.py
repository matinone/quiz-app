import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories.answer_options_factory import AnswerOptionFactory
from app.tests.factories.question_factory import QuestionFactory


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_create_answer_options(
    client: AsyncClient, db_session: AsyncSession, cases: str
):
    if cases == "found":
        question = await QuestionFactory.create()
        question_id = question.id
    else:
        question_id = 123

    answer_data = {"content": "This is the answer", "is_correct": True}
    response = await client.post(
        f"/api/questions/{question_id}/options", json=answer_data
    )

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_201_CREATED
        created_answer = response.json()
        for key in answer_data:
            assert created_answer[key] == answer_data[key]


@pytest.mark.parametrize("cases", ["found", "not_found"])
async def test_get_answer_options(
    client: AsyncClient,
    db_session: AsyncSession,
    cases: str,
):
    if cases == "found":
        question = await QuestionFactory.create()
        answer_options = await AnswerOptionFactory.create_batch(5, question=question)
        question_id = question.id
    else:
        question_id = 123

    response = await client.get(f"/api/questions/{question_id}/options")

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK

        returned_options = response.json()
        assert len(returned_options) == len(answer_options)

        # sort questions by id so they can be iterated simultaneously
        answer_options = sorted(answer_options, key=lambda d: d.id)
        returned_options = sorted(returned_options, key=lambda d: d["id"])

        for created, returned in zip(answer_options, returned_options):
            for key in returned:
                assert returned[key] == getattr(created, key)
