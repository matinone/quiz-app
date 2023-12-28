from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas import QuestionReturn


class QuizBase(BaseModel):
    title: str
    description: str | None = None
    created_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    # not forced to always update all the fields
    title: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class QuizReturn(QuizBase):
    id: int
    created_at: datetime
    updated_at: datetime


class QuizWithQuestions(QuizReturn):
    questions: list[QuestionReturn]
