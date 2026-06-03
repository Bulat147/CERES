from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.locker_station import LockerStation
from app.schemas.locker_station import LockerStationCreate, LockerStationUpdate, LockerStationResponse

router = APIRouter()

crud_locker_station = CRUDBase(LockerStation)


@router.get("/", response_model=List[LockerStationResponse])
async def read_locker_stations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список постоматов.
    """
    stations = await crud_locker_station.get_multi(db, skip=skip, limit=limit)
    return stations


@router.post("/", response_model=LockerStationResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/{station_id}", response_model=LockerStationResponse)
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
    return station


@router.put("/{station_id}", response_model=LockerStationResponse)
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


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
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