import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.tests.factories.user_factory import UserFactory


@pytest.mark.parametrize("cases", ["valid", "not_user", "wrong_password"])
async def test_get_access_token_valid(
    client: AsyncClient,
    db_session: AsyncSession,
    cases: str,
):
    username = "random_name"
    password = "123456789"

    if cases != "not_user":
        await UserFactory.create(
            username=username, password_hash=get_password_hash(password)
        )

    form_data = {"username": username, "password": password}
    if cases == "wrong_password":
        form_data["password"] = "wrong_password"

    response = await client.post("/api/tokens", data=form_data)

    if cases != "valid":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    else:
        assert response.status_code == status.HTTP_201_CREATED

        token = response.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"


@pytest.mark.parametrize("cases", ["valid", "existing_username", "existing_email"])
async def test_register_user(client: AsyncClient, db_session: AsyncSession, cases: str):
    user_info = {"username": "user", "email": "user@example.com", "password": "123456"}

    if cases == "existing_username":
        await UserFactory.create(username=user_info["username"])
    elif cases == "existing_email":
        await UserFactory.create(email=user_info["email"])

    response = await client.post("/api/register", json=user_info)
    if cases != "valid":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    else:
        assert response.status_code == status.HTTP_201_CREATED

        created_user = response.json()
        for key in ["username", "email"]:
            assert created_user[key] == user_info[key]
