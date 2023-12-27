from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    # not forced to always update all the fields
    username: str | None
    email: EmailStr | None
    password: str | None

    model_config = ConfigDict(from_attributes=True)


class UserReturn(UserBase):
    id: int
    created_at: datetime
    last_login: datetime
