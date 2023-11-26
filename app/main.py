from fastapi import FastAPI

from app.api.api import api_router
from app.core.custom_logging import configure_logger
from app.core.settings import get_settings
from app.models.database import init_db

logger = configure_logger()

app = FastAPI(title="Quiz App")
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import asyncio  # noqa: I001
    import uvicorn

    if get_settings().ENVIRONMENT != "prod":
        asyncio.run(init_db())
        reload = True
    else:
        logger.info("Not creating database tables")
        reload = False

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=reload)
