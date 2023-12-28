from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.settings import Settings, get_settings
from app.schemas import TokenPayload

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decode_token(token: str, settings: Settings) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # raises ValidationError if the payload is not valid
        token_data = TokenPayload(**payload)
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token expired"
        ) from exc
    except (JWTError, ValidationError) as exc:
        # any HTTP status code 401 "UNAUTHORIZED" is supposed to also
        # return a WWW-Authenticate header
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return token_data


def create_access_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
