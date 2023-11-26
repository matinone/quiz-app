from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Quiz App"
    ENVIRONMENT: str = "dev"

    ECHO_SQL: bool = False
    USE_ALEMBIC: bool = False
    USE_SQLITE: bool = False

    DB_BASE: str = "postgresql+asyncpg"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self) -> str:
        """
        A function is needed (instead of directly creating the URL
        as an additional attribute) to make sure that the values from the .env file
        are used (instead of the default values).
        """
        if self.USE_SQLITE:
            return "sqlite+aiosqlite:///./sqlite_dev.db"

        return (
            f"{self.DB_BASE}://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
