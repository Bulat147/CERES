from app.api.users import router as users_router
from app.api.locker_stations import router as locker_stations_router
from app.api.locker_cells import router as locker_cells_router
from app.api.rentals import router as rentals_router
from app.api.payment_methods import router as payment_methods_router
from app.api.payments import router as payments_router
from app.api.cell_events import router as cell_events_router
from app.api.hardware_events import router as hardware_events_router

__all__ = [
    "users_router",
    "locker_stations_router",
    "locker_cells_router",
    "rentals_router",
    "payment_methods_router",
    "payments_router",
    "cell_events_router",
    "hardware_events_router",
]