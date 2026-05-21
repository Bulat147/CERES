from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.hardware_event import HardwareEvent
from app.models.locker_cell import LockerCell
from app.schemas.hardware_event import HardwareEventCreate, HardwareEventResponse

router = APIRouter()

crud_hardware_event = CRUDBase(HardwareEvent)


@router.get("/", response_model=List[HardwareEventResponse])
async def read_hardware_events(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    cell_id: UUID = None,
    processed: bool = None,
):
    """
    Получить список аппаратных событий.
    Можно отфильтровать по cell_id, processed.
    """
    query = select(HardwareEvent)
    if cell_id:
        query = query.where(HardwareEvent.cell_id == cell_id)
    if processed is not None:
        query = query.where(HardwareEvent.processed == processed)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    return events


@router.post("/", response_model=HardwareEventResponse, status_code=status.HTTP_201_CREATED)
async def create_hardware_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_in: HardwareEventCreate,
):
    """
    Создать новое аппаратное событие.
    """
    # Проверяем существование ячейки
    cell = await db.get(LockerCell, event_in.cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найдена",
        )
    event_data = event_in.model_dump()
    event = await crud_hardware_event.create(db, obj_in=event_data)
    return event


@router.get("/{event_id}", response_model=HardwareEventResponse)
async def read_hardware_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить аппаратное событие по ID.
    """
    event = await crud_hardware_event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие не найдено",
        )
    return event


@router.put("/{event_id}/mark-processed", response_model=HardwareEventResponse)
async def mark_hardware_event_processed(
    *,
    db: AsyncSession = Depends(get_db),
    event_id: UUID,
):
    """
    Отметить аппаратное событие как обработанное.
    """
    event = await crud_hardware_event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие не найдено",
        )
    event.processed = True
    await db.commit()
    await db.refresh(event)
    return event