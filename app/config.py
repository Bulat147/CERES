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

    # Настройки базы данных
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite или postgresql
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "app")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "app")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ceres_db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "sqlite:///./ceres.db")

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()