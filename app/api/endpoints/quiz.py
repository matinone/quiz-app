from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

import app.models as models
import app.schemas as schemas
from app.api.dependencies import get_current_user
from app.models.database import AsyncSessionDep

router = APIRouter(prefix="/quizzes", tags=["quiz"])


async def get_quiz_from_id(quiz_id: int, db: AsyncSessionDep) -> models.Quiz:
    quiz = await models.Quiz.get(db=db, id=quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    return quiz


async def get_quiz_check_user(
    quiz_id: int,
    user: Annotated[models.User, Depends(get_current_user)],
    db: AsyncSessionDep,
) -> models.Quiz:
    quiz = await models.Quiz.get(db=db, id=quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    if quiz.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz does not belong to current user",
        )

    return quiz


@router.post(
    "",
    response_model=schemas.QuizReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz",
    response_description="The new created quiz",
)
async def create_quiz(
    db: AsyncSessionDep,
    quiz: schemas.QuizCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> Any:
    quiz.created_by = current_user.id
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


@router.get(
    "/{quiz_id}",
    response_model=schemas.QuizReturn,
    status_code=status.HTTP_200_OK,
    summary="Get quiz by id",
    response_description="The requested quiz (if it exists)",
)
async def get_quiz(quiz: Annotated[models.Quiz, Depends(get_quiz_from_id)]) -> Any:
    return quiz


@router.put(
    "/{quiz_id}",
    response_model=schemas.QuizReturn,
    status_code=status.HTTP_200_OK,
    summary="Update quiz by id",
    response_description="The updated quiz (if it exists)",
)
async def update_quiz(
    update_data: schemas.QuizUpdate,
    quiz: Annotated[models.Quiz, Depends(get_quiz_check_user)],
    db: AsyncSessionDep,
) -> Any:
    updated_quiz = await models.Quiz.update(db=db, current=quiz, new=update_data)

    return updated_quiz


@router.delete(
    "/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quiz by id",
)
async def delete_quiz(
    quiz: Annotated[models.Quiz, Depends(get_quiz_check_user)],
    db: AsyncSessionDep,
) -> None:
    await models.Quiz.delete(db=db, db_obj=quiz)
    # body will be empty when using status code 204


@router.post(
    "/{quiz_id}/questions",
    response_model=schemas.QuestionReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Create a question associated to the quiz",
    response_description="The created question",
)
async def create_question_for_quiz(
    quiz: Annotated[models.Quiz, Depends(get_quiz_check_user)],
    question: schemas.QuestionCreate,
    db: AsyncSessionDep,
) -> Any:
    question.quiz_id = quiz.id
    try:
        new_question = await models.Question.create(db=db, question=question)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        ) from exc

    return new_question


@router.get(
    "/{quiz_id}/questions",
    response_model=list[schemas.QuestionReturn],
    status_code=status.HTTP_200_OK,
    summary="Get all questions associated to the quiz",
    response_description="The list of questions associated to the quiz",
)
async def get_all_questions_from_quiz(quiz_id: int, db: AsyncSessionDep) -> Any:
    quiz = await models.Quiz.get_with_questions(db=db, id=quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    return quiz.questions
