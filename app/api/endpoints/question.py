from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

import app.models as models
import app.schemas as schemas
from app.api.dependencies import get_current_user
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


async def get_question_check_user(
    question: Annotated[models.Question, Depends(get_question_from_id)],
    user: Annotated[models.User, Depends(get_current_user)],
    db: AsyncSessionDep,
) -> models.Question:
    quiz_author_id = await models.Quiz.get_quiz_created_by(db=db, id=question.quiz_id)
    if quiz_author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz does not belong to current user",
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
    question: Annotated[models.Question, Depends(get_question_check_user)],
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
    question: Annotated[models.Question, Depends(get_question_check_user)],
    db: AsyncSessionDep,
) -> None:
    await models.Question.delete(db=db, db_obj=question)
    # body will be empty when using status code 204


# TODO: only the quiz author should be able to add answer options to a question
@router.post(
    "/{question_id}/options",
    response_model=schemas.AnswerOptionReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Add an answer option to the question",
    response_description="The created answer option",
)
async def add_answer_option(
    question_id: int,
    answer: schemas.AnswerOptionCreate,
    db: AsyncSessionDep,
) -> Any:
    answer.question_id = question_id
    try:
        created_answer = await models.AnswerOption.create(db=db, option=answer)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        ) from exc

    return created_answer


@router.get(
    "/{question_id}/options",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.AnswerOptionReturn],
    summary="Get all answer options associated to the question",
    response_description="The list of answer options associated to the question",
)
async def get_question_answer_options(
    question_id: int,
    db: AsyncSessionDep,
) -> Any:
    question = await models.Question.get_with_answers(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    return question.answer_options
