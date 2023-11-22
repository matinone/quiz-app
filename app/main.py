from fastapi import FastAPI

from app.api.api import api_router
from app.core.settings import get_settings
from app.models.database import init_db

app = FastAPI(title="Quiz App")
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import asyncio  # noqa: I001
    import uvicorn

    if get_settings().ENVIRONMENT != "prod":
        asyncio.run(init_db())

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
