from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Quiz App"
    ENVIRONMENT: str = "dev"
    DB_URL: str = "sqlite+aiosqlite:///./sqlite_dev.db"
    ECHO_SQL: bool = False
    USE_ALEMBIC: bool = False

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
