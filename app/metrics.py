import asyncio
from typing import Optional

from prometheus_client import Counter, Gauge
from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings

DB_REQUESTS = Counter(
    "ceres_db_requests_total",
    "Запросы к базе данных",
    ["status"],
)

RENTALS_CREATED = Counter(
    "ceres_rentals_created_total",
    "Количество созданных аренд",
)
RENTALS_STARTED = Counter(
    "ceres_rentals_started_total",
    "Количество начатых аренд (ячейка открыта)",
)
PAYMENTS_CREATED = Counter(
    "ceres_payments_created_total",
    "Количество созданных платежей",
    ["status"],
)

ACTIVE_RENTALS = Gauge(
    "ceres_active_rentals",
    "Аренды в статусе ACTIVE",
)
AVAILABLE_CELLS = Gauge(
    "ceres_available_cells",
    "Свободные ячейки (AVAILABLE)",
)

_metrics_task: Optional[asyncio.Task] = None


def instrument_db_engine(async_engine: AsyncEngine) -> None:
    if not settings.ENABLE_METRICS:
        return

    sync_engine = async_engine.sync_engine

    @event.listens_for(sync_engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        DB_REQUESTS.labels(status="success").inc()

    @event.listens_for(sync_engine, "handle_error")
    def _handle_db_error(exception_context):
        DB_REQUESTS.labels(status="error").inc()


async def refresh_business_gauges() -> None:
    from app.db.database import AsyncSessionLocal
    from app.models.locker_cell import LockerCell
    from app.models.rental import Rental

    async with AsyncSessionLocal() as session:
        active_count = await session.scalar(
            select(func.count()).select_from(Rental).where(Rental.status == "ACTIVE")
        )
        available_count = await session.scalar(
            select(func.count()).select_from(LockerCell).where(LockerCell.status == "AVAILABLE")
        )
        ACTIVE_RENTALS.set(active_count or 0)
        AVAILABLE_CELLS.set(available_count or 0)


async def _metrics_refresh_loop() -> None:
    while True:
        try:
            await refresh_business_gauges()
        except Exception:
            pass
        await asyncio.sleep(30)


def start_business_metrics_refresh() -> Optional[asyncio.Task]:
    if not settings.ENABLE_METRICS:
        return None
    return asyncio.create_task(_metrics_refresh_loop())


async def stop_business_metrics_refresh(task: Optional[asyncio.Task]) -> None:
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
