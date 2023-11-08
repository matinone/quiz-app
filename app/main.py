from fastapi import FastAPI

from app.core.settings import get_settings
from app.models.database import init_db

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import asyncio  # noqa: I001
    import uvicorn

    if get_settings().ENVIRONMENT != "prod":
        asyncio.run(init_db())

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
