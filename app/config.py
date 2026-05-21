import os
from typing import Optional, List

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator, AnyHttpUrl


class Settings(BaseSettings):
    # Базовая конфигурация
    PROJECT_NAME: str = "CERES Locker Rental API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Настройки базы данных
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite или postgresql
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "app")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "app")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ceres_db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "sqlite:///./ceres.db")

    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v

        database_type = values.get("DATABASE_TYPE", "sqlite")

        if database_type == "postgresql":
            return str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT"),
                path=f"{values.get('POSTGRES_DB') or ''}",
            ))
        else:
            # SQLite для локальной разработки
            return values.get("SQLITE_DB_PATH", "sqlite+aiosqlite:///./ceres.db")

    # JWT настройки (если понадобится для аутентификации)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    # CORS настройки
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v: str) -> list:
        """Парсинг строки CORS_ORIGINS в список."""
        if not v:
            return []
        return [origin.strip() for origin in v.split(",")]

    # Настройки платежей
    YOOKASSA_SHOP_ID: Optional[str] = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: Optional[str] = os.getenv("YOOKASSA_SECRET_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()