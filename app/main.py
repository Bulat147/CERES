from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import main_router
from app.api import users, locker_stations, locker_cells, rentals, payment_methods, payments, cell_events, hardware_events
from app.config import settings
from app.logger import setup_logging
from app.middlewares import setup_middlewares
from app.db.database import init_db
from app.metrics import start_business_metrics_refresh, stop_business_metrics_refresh


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для управления жизненным циклом приложения.
    """
    # Настройка логирования при запуске
    setup_logging(level="DEBUG" if settings.DEBUG else "INFO")

    # Инициализация базы данных (создание таблиц, если не используются миграции)
    # В продакшене используйте Alembic миграции
    # await init_db()

    metrics_task = start_business_metrics_refresh()

    yield

    await stop_business_metrics_refresh(metrics_task)


app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка middleware
setup_middlewares(app)

# Подключаем роутеры
app.include_router(main_router)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(locker_stations.router, prefix="/api/v1/locker-stations", tags=["locker-stations"])
app.include_router(locker_cells.router, prefix="/api/v1/locker-cells", tags=["locker-cells"])
app.include_router(rentals.router, prefix="/api/v1/rentals", tags=["rentals"])
app.include_router(payment_methods.router, prefix="/api/v1/payment-methods", tags=["payment-methods"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(cell_events.router, prefix="/api/v1/cell-events", tags=["cell-events"])
app.include_router(hardware_events.router, prefix="/api/v1/hardware-events", tags=["hardware-events"])

if settings.ENABLE_METRICS:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
