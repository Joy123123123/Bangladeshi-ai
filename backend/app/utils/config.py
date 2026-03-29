"""
Application configuration loaded from environment variables.
"""

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Bangladeshi-ai"
    app_env: str = "development"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # AI API Keys
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    grok_api_key: str = ""

    # Default model
    default_ai_model: str = "gemini"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/bangladeshi_ai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security / JWT
    jwt_secret: str = "change_this_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate limiting
    rate_limit_anonymous: int = 20
    rate_limit_authenticated: int = 60

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v


settings = Settings()
