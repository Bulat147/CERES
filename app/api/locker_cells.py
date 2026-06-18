from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.deps import get_current_user
from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.locker_cell import LockerCell
from app.models.locker_station import LockerStation
from app.schemas.locker_cell import LockerCellCreate, LockerCellUpdate, LockerCellResponse

router = APIRouter()

crud_locker_cell = CRUDBase(LockerCell)


@router.get("/", response_model=List[LockerCellResponse], dependencies=[Depends(get_current_user)])
async def read_locker_cells(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    station_id: UUID = None,
):
    """
    Получить список ячеек.
    Можно отфильтровать по station_id.
    """
    query = select(LockerCell)
    if station_id:
        query = query.where(LockerCell.station_id == station_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    cells = result.scalars().all()
    return cells


@router.post("/", response_model=LockerCellResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_locker_cell(
    *,
    db: AsyncSession = Depends(get_db),
    cell_in: LockerCellCreate,
):
    """
    Создать новую ячейку.
    """
    # Проверяем существование постомата
    station = await db.get(LockerStation, cell_in.station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Постомат не найден",
        )
    cell_data = cell_in.model_dump()
    cell = await crud_locker_cell.create(db, obj_in=cell_data)
    return cell


@router.get("/{cell_id}", response_model=LockerCellResponse, dependencies=[Depends(get_current_user)])
async def read_locker_cell(
    cell_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить ячейку по ID.
    """
    cell = await crud_locker_cell.get(db, id=cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найден",
        )
    return cell


@router.put("/{cell_id}", response_model=LockerCellResponse, dependencies=[Depends(get_current_user)])
async def update_locker_cell(
    *,
    db: AsyncSession = Depends(get_db),
    cell_id: UUID,
    cell_in: LockerCellUpdate,
):
    """
    Обновить данные ячейки.
    """
    cell = await crud_locker_cell.get(db, id=cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найден",
        )
    update_data = cell_in.model_dump(exclude_unset=True)
    if update_data.get("station_id"):
        # Проверяем существование нового постомата
        station = await db.get(LockerStation, update_data["station_id"])
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Постомат не найден",
            )
    cell = await crud_locker_cell.update(db, db_obj=cell, obj_in=update_data)
    return cell


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def delete_locker_cell(
    *,
    db: AsyncSession = Depends(get_db),
    cell_id: UUID,
):
    """
    Удалить ячейку.
    """
    cell = await crud_locker_cell.get(db, id=cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найден",
        )
    await crud_locker_cell.delete(db, id=cell_id)
    return None