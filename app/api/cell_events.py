from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.cell_event import CellEvent
from app.models.locker_cell import LockerCell
from app.schemas.cell_event import CellEventCreate, CellEventResponse

router = APIRouter()

crud_cell_event = CRUDBase(CellEvent)


@router.get("/", response_model=List[CellEventResponse])
async def read_cell_events(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    cell_id: UUID = None,
    rental_id: UUID = None,
):
    """
    Получить список событий ячеек.
    Можно отфильтровать по cell_id, rental_id.
    """
    query = select(CellEvent)
    if cell_id:
        query = query.where(CellEvent.cell_id == cell_id)
    if rental_id:
        query = query.where(CellEvent.rental_id == rental_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    return events


@router.post("/", response_model=CellEventResponse, status_code=status.HTTP_201_CREATED)
async def create_cell_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_in: CellEventCreate,
):
    """
    Создать новое событие ячейки.
    """
    # Проверяем существование ячейки
    cell = await db.get(LockerCell, event_in.cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найдена",
        )
    event_data = event_in.model_dump()
    event = await crud_cell_event.create(db, obj_in=event_data)
    return event


@router.get("/{event_id}", response_model=CellEventResponse)
async def read_cell_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить событие ячейки по ID.
    """
    event = await crud_cell_event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие не найдено",
        )
    return event