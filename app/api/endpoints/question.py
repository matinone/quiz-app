from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

import app.models as models
import app.schemas as schemas
from app.models.database import AsyncSessionDep

router = APIRouter(prefix="/questions", tags=["question"])


async def get_question_from_id(
    question_id: int, db: AsyncSessionDep
) -> models.Question:
    question = await models.Question.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    return question


@router.get(
    "/{question_id}",
    response_model=schemas.QuestionReturn,
    status_code=status.HTTP_200_OK,
    summary="Get question by id",
    response_description="The requested question (if it exists)",
)
async def get_question(
    question: Annotated[models.Question, Depends(get_question_from_id)]
) -> Any:
    return question


@router.put(
    "/{question_id}",
    response_model=schemas.QuestionReturn,
    status_code=status.HTTP_200_OK,
    summary="Update question by id",
    response_description="The updated question (if it exists)",
)
async def update_question(
    update_data: schemas.QuestionUpdate,
    question: Annotated[models.Question, Depends(get_question_from_id)],
    db: AsyncSessionDep,
) -> Any:
    updated_question = await models.Question.update(
        db=db, current=question, new=update_data
    )

    return updated_question


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quiz by id",
)
async def delete_question(
    question: Annotated[models.Question, Depends(get_question_from_id)],
    db: AsyncSessionDep,
) -> None:
    await models.Question.delete(db=db, db_obj=question)
    # body will be empty when using status code 204
