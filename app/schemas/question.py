from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionBase(BaseModel):
    quiz_id: int
    content: str
    type: str
    points: int

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    # not forced to always update all the fields
    quiz_id: int | None = None
    content: str | None = None
    type: str | None = None
    points: int | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionReturn(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime
