from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.core.settings import Settings, get_settings
from app.models.database import AsyncSessionDep
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/tokens")


async def get_current_user(
    db: AsyncSessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    token_data = decode_token(token=token, settings=settings)
    user = await User.get(db=db, id=int(token_data.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
