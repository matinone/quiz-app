from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class QuestionType(str, Enum):
    open = "open"
    multiple_choice = "multiple_choice"
    true_false = "true_false"


class QuestionBase(BaseModel):
    content: str
    type: QuestionType = QuestionType.open
    points: int = 1

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(QuestionBase):
    quiz_id: int | None = None


class QuestionUpdate(BaseModel):
    # not forced to always update all the fields
    content: str | None = None
    type: QuestionType | None = None
    points: int | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionReturn(QuestionBase):
    id: int
    quiz_id: int
    created_at: datetime
    updated_at: datetime
