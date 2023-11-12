from typing import Any

from fastapi import APIRouter, status

import app.models as models
import app.schemas as schemas
from app.models.database import AsyncSessionDep
from app.models.question import Question  # noqa: F401

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post(
    "/",
    response_model=schemas.QuizReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz",
    response_description="The new created quiz",
)
async def create_quiz(db: AsyncSessionDep, quiz: schemas.QuizCreate) -> Any:
    new_quiz = await models.Quiz.create(db=db, quiz=quiz)
    return new_quiz
