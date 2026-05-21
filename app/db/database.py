from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.config import settings

# Определяем движок базы данных в зависимости от типа
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite требует специальной настройки для асинхронной работы
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False} if "aiosqlite" in settings.DATABASE_URL else {},
        poolclass=StaticPool if ":memory:" in settings.DATABASE_URL else None,
    )
else:
    # PostgreSQL или другие базы данных
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# Dependency для получения сессии базы данных
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Асинхронная зависимость для получения сессии базы данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализация базы данных (создание таблиц).
    В продакшене используйте Alembic миграции.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
