"""Application configuration module.

This module defines application settings loaded from environment variables
and .env file using Pydantic BaseSettings.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration.

    Attributes:
        APP_NAME: Application name.
        APP_VERSION: Application version.
        DEBUG: Debug mode flag.
        DATABASE_URL: Database connection string.
        SECRET_KEY: JWT secret key for token generation.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time.
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time.
        LOG_LEVEL: Logging level.
        CORS_ORIGINS: Allowed CORS origins.
        CORS_ALLOW_CREDENTIALS: Allow credentials in CORS requests.
        CORS_ALLOW_METHODS: Allowed HTTP methods for CORS.
        CORS_ALLOW_HEADERS: Allowed headers for CORS.
    """

    APP_NAME: str = "BookStore API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./bookstore.db"
    # MariaDB 예시: "mysql+pymysql://user:password@localhost/bookStoreDb"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"  # Docker 전용 환경 변수 허용


settings = Settings()
