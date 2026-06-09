import os
from typing import Optional, List

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator, ValidationInfo


class Settings(BaseSettings):
    # Базовая конфигурация
    PROJECT_NAME: str = "CERES Locker Rental API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Настройки базы данных (postgresql по умолчанию; sqlite — для локальных экспериментов)
    DATABASE_TYPE: str = "postgresql"
    POSTGRES_SERVER: str = "85.209.9.46"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "app"
    POSTGRES_DB: str = "main"
    POSTGRES_PORT: int = 5432
    SQLITE_DB_PATH: str = "sqlite+aiosqlite:///./ceres.db"

    # true — при старте контейнера выполняется alembic upgrade head (создание/обновление таблиц)
    RUN_DB_MIGRATIONS: bool = os.getenv("RUN_DB_MIGRATIONS", "true").lower() in ("1", "true", "yes")

    # Prometheus-метрики на /metrics
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() in ("1", "true", "yes")

    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v

        data = info.data
        database_type = data.get("DATABASE_TYPE", "sqlite")

        if database_type == "postgresql":
            return str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_SERVER"),
                port=data.get("POSTGRES_PORT"),
                path=f"{data.get('POSTGRES_DB') or ''}",
            ))
        else:
            return data.get("SQLITE_DB_PATH", "sqlite+aiosqlite:///./ceres.db")

    # JWT настройки (если понадобится для аутентификации)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "false").lower() == "true"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсинг строки CORS_ORIGINS в список."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Настройки платежей
    YOOKASSA_SHOP_ID: Optional[str] = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: Optional[str] = os.getenv("YOOKASSA_SECRET_KEY")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()