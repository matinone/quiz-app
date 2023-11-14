from typing import Annotated, Any

from fastapi import APIRouter, Query, status

import app.models as models
import app.schemas as schemas
from app.models.database import AsyncSessionDep
from app.models.question import Question  # noqa: F401

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "",
    response_model=schemas.QuizReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz",
    response_description="The new created quiz",
)
async def create_quiz(db: AsyncSessionDep, quiz: schemas.QuizCreate) -> Any:
    new_quiz = await models.Quiz.create(db=db, quiz=quiz)
    return new_quiz


@router.get(
    "",
    response_model=list[schemas.QuizReturn],
    status_code=status.HTTP_200_OK,
    summary="Get available quizzes sorted by creation date",
    response_description="The list of quizzes",
)
async def get_quizzes(
    db: AsyncSessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 25,
) -> Any:
    quizzes = await models.Quiz.get_multiple(offset=offset, limit=limit, db=db)
    return quizzes
