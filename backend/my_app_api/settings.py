import os
from functools import lru_cache

from pydantic import ConfigDict, PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: str = os.getenv("ALEMBIC_DATABASE_URL", "postgresql://postgres:12345@localhost:5432/gasdynamicdb")
    ROOT_PATH: str = "/" + os.getenv("APP_NAME", "")

    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
