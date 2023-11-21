from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

import app.models as models
import app.schemas as schemas
from app.models.database import AsyncSessionDep
from app.models.question import Question  # noqa: F401

router = APIRouter(prefix="/question", tags=["question"])


async def get_question_from_id(question_id: int, db: AsyncSessionDep):
    question = await models.Question.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    return question


@router.post(
    "",
    response_model=schemas.QuestionReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question",
    response_description="The new created question",
)
async def create_question(db: AsyncSessionDep, question: schemas.QuestionCreate) -> Any:
    try:
        new_question = await models.Question.create(db=db, question=question)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid quiz_id"
        ) from exc

    return new_question
