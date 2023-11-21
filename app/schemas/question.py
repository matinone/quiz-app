from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class QuestionType(str, Enum):
    open = "open"
    multiple_choice = "multiple_choice"
    true_false = "true_false"


class QuestionBase(BaseModel):
    quiz_id: int
    content: str
    type: QuestionType = QuestionType.open
    points: int = 1

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
