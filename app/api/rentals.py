from typing import List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.rental import Rental
from app.models.user import User
from app.models.locker_cell import LockerCell
from app.schemas.rental import RentalCreate, RentalUpdate, RentalResponse
from app.metrics import RENTALS_CREATED, RENTALS_STARTED

router = APIRouter()

crud_rental = CRUDBase(Rental)


@router.get("/", response_model=List[RentalResponse])
async def read_rentals(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: UUID = None,
    cell_id: UUID = None,
    status: str = None,
):
    """
    Получить список аренд.
    Можно отфильтровать по user_id, cell_id, status.
    """
    query = select(Rental)
    if user_id:
        query = query.where(Rental.user_id == user_id)
    if cell_id:
        query = query.where(Rental.cell_id == cell_id)
    if status:
        query = query.where(Rental.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rentals = result.scalars().all()
    return rentals


@router.post("/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    *,
    db: AsyncSession = Depends(get_db),
    rental_in: RentalCreate,
):
    """
    Создать новую аренду.
    """
    # Проверяем существование пользователя и ячейки
    user = await db.get(User, rental_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    cell = await db.get(LockerCell, rental_in.cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найдена",
        )
    # Проверяем, что ячейка доступна
    if cell.status != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ячейка недоступна для аренды",
        )
    rental_data = rental_in.model_dump()
    rental = await crud_rental.create(db, obj_in=rental_data)
    # Обновляем статус ячейки на RESERVED
    cell.status = "RESERVED"
    await db.commit()
    RENTALS_CREATED.inc()
    return rental


@router.get("/{rental_id}", response_model=RentalResponse)
async def read_rental(
    rental_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить аренду по ID.
    """
    rental = await crud_rental.get(db, id=rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    return rental


@router.put("/{rental_id}", response_model=RentalResponse)
async def update_rental(
    *,
    db: AsyncSession = Depends(get_db),
    rental_id: UUID,
    rental_in: RentalUpdate,
):
    """
    Обновить данные аренды.
    """
    rental = await crud_rental.get(db, id=rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    update_data = rental_in.model_dump(exclude_unset=True)
    rental = await crud_rental.update(db, db_obj=rental, obj_in=update_data)
    return rental


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental(
    *,
    db: AsyncSession = Depends(get_db),
    rental_id: UUID,
):
    """
    Удалить аренду.
    """
    rental = await crud_rental.get(db, id=rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    await crud_rental.delete(db, id=rental_id)
    return None


@router.post("/{rental_id}/start", response_model=RentalResponse)
async def start_rental(
    *,
    db: AsyncSession = Depends(get_db),
    rental_id: UUID,
):
    """
    Начать аренду (открыть ячейку).
    """
    rental = await crud_rental.get(db, id=rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    if rental.status != "CREATED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аренда уже начата или завершена",
        )
    cell = await db.get(LockerCell, rental.cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найдена",
        )
    # Обновляем статусы
    rental.status = "ACTIVE"
    rental.opened_at = datetime.utcnow()
    rental.started_at = datetime.utcnow()
    cell.status = "ACTIVE"
    await db.commit()
    await db.refresh(rental)
    RENTALS_STARTED.inc()
    return rental


@router.post("/{rental_id}/close", response_model=RentalResponse)
async def close_rental(
    *,
    db: AsyncSession = Depends(get_db),
    rental_id: UUID,
):
    """
    Закрыть аренду (пользователь закрыл дверь).
    """
    rental = await crud_rental.get(db, id=rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    if rental.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аренда не активна",
        )
    cell = await db.get(LockerCell, rental.cell_id)
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ячейка не найдена",
        )
    # Обновляем статусы
    rental.status = "WAITING_CLOSE"
    rental.closed_at = datetime.utcnow()
    cell.status = "PAYMENT"
    await db.commit()
    await db.refresh(rental)
    return rental