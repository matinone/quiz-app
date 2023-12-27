from pydantic import BaseModel, ConfigDict


class AnswerOptionBase(BaseModel):
    content: str
    is_correct: bool = False

    model_config = ConfigDict(from_attributes=True)


class AnswerOptionCreate(AnswerOptionBase):
    question_id: int | None = None


class AnswerOptionUpdate(BaseModel):
    # not forced to always update all the fields
    content: str | None = None
    is_correct: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class AnswerOptionReturn(AnswerOptionBase):
    id: int
    question_id: int
