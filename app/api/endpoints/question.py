from fastapi import APIRouter, HTTPException, status

import app.models as models
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
