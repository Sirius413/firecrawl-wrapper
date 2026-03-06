import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY")
    FIRECRAWL_API_URL: str = "http://api:3002/v1"
    APP_NAME: str = "Firecrawl Wrapper"
    DEBUG : bool = False

    class Config:
        env_file = ".env"

settings = Settings()
