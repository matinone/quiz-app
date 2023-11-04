from pydantic import BaseModel, ConfigDict

from datetime import datetime


class QuestionBase(BaseModel):
    content: str
    type: str
    points: int

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(QuestionBase):
    # not forced to always update all the fields
    content: str | None
    type: str | None
    points: int | None


class QuestionReturn(QuestionBase):
    id: int
    quiz_id: int
    created_at: datetime
    updated_at: datetime
