from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import app.models as models
import app.schemas as schemas
from app.core.security import create_access_token, verify_password
from app.models.database import AsyncSessionDep

router = APIRouter(prefix="", tags=["login"])


@router.post(
    "/tokens",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    summary="Get a new access token",
)
async def get_access_token_from_username(
    db: AsyncSessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """
    Get an OAuth2 access token from a user logging in with a username and password,
    to use in future requests as an authenticated user.
    """
    user = await models.User.get_by_username(db=db, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    if not verify_password(
        plain_password=form_data.password, hashed_password=user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    response = {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
    }
    return response


@router.post(
    "/register",
    response_model=schemas.UserReturn,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(db: AsyncSessionDep, user: schemas.UserCreate):
    new_user = await models.User.get_by_username(db=db, username=user.username)
    if new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    new_user = await models.User.get_by_email(db=db, email=user.email)
    if new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    new_user = await models.User.create(db=db, user=user)
    return new_user
