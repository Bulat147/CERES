from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.auth.deps import get_current_user
from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.locker_station import LockerStation
from app.models.locker_cell import LockerCell
from app.schemas.locker_station import LockerStationCreate, LockerStationUpdate, LockerStationResponse

router = APIRouter()

crud_locker_station = CRUDBase(LockerStation)


async def _apply_cell_counts(stations: List[LockerStation], db: AsyncSession) -> None:
    if not stations:
        return
    station_ids = [s.id for s in stations]
    stats_query = select(
        LockerCell.station_id,
        func.count().label("total"),
        func.sum(case((LockerCell.status == "AVAILABLE", 1), else_=0)).label("free"),
    ).where(LockerCell.station_id.in_(station_ids)).group_by(LockerCell.station_id)
    result = await db.execute(stats_query)
    stats = {row.station_id: {"total": row.total, "free": row.free} for row in result}
    for station in stations:
        s = stats.get(station.id, {"total": 0, "free": 0})
        station.total_cells = s["total"]
        station.free_cells = s["free"]
        station.occupied_cells = s["total"] - s["free"]


@router.get("/", response_model=List[LockerStationResponse], dependencies=[Depends(get_current_user)])
async def read_locker_stations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список постоматов.
    """
    stations = await crud_locker_station.get_multi(db, skip=skip, limit=limit)
    await _apply_cell_counts(stations, db)
    return stations


@router.post("/", response_model=LockerStationResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_locker_station(
    *,
    db: AsyncSession = Depends(get_db),
    station_in: LockerStationCreate,
):
    """
    Создать новый постомат.
    """
    station_data = station_in.model_dump()
    station = await crud_locker_station.create(db, obj_in=station_data)
    return station


@router.get("/{station_id}", response_model=LockerStationResponse, dependencies=[Depends(get_current_user)])
async def read_locker_station(
    station_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить постомат по ID.
    """
    station = await crud_locker_station.get(db, id=station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Постомат не найден",
        )
    await _apply_cell_counts([station], db)
    return station


@router.put("/{station_id}", response_model=LockerStationResponse, dependencies=[Depends(get_current_user)])
async def update_locker_station(
    *,
    db: AsyncSession = Depends(get_db),
    station_id: UUID,
    station_in: LockerStationUpdate,
):
    """
    Обновить данные постомата.
    """
    station = await crud_locker_station.get(db, id=station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Постомат не найден",
        )
    update_data = station_in.model_dump(exclude_unset=True)
    station = await crud_locker_station.update(db, db_obj=station, obj_in=update_data)
    return station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def delete_locker_station(
    *,
    db: AsyncSession = Depends(get_db),
    station_id: UUID,
):
    """
    Удалить постомат.
    """
    station = await crud_locker_station.get(db, id=station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Постомат не найден",
        )
    await crud_locker_station.delete(db, id=station_id)
    return None
