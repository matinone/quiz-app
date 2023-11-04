from pydantic import BaseModel, ConfigDict

from datetime import datetime


class QuizBase(BaseModel):
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class QuizCreate(QuizBase):
    pass


class QuizUpdate(QuizBase):
    # not forced to always update the title
    title: str | None


class QuizReturn(QuizBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # TODO: add created_by field once users table is available