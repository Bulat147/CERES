from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.payment import Payment
from app.models.rental import Rental
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse

router = APIRouter()

crud_payment = CRUDBase(Payment)


@router.get("/", response_model=List[PaymentResponse])
async def read_payments(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    rental_id: UUID = None,
    user_id: UUID = None,
    status: str = None,
):
    """
    Получить список платежей.
    Можно отфильтровать по rental_id, user_id, status.
    """
    query = select(Payment)
    if rental_id:
        query = query.where(Payment.rental_id == rental_id)
    if user_id:
        query = query.where(Payment.user_id == user_id)
    if status:
        query = query.where(Payment.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    payments = result.scalars().all()
    return payments


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_in: PaymentCreate,
):
    """
    Создать новый платеж.
    """
    # Проверяем существование аренды и пользователя
    rental = await db.get(Rental, payment_in.rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аренда не найдена",
        )
    user = await db.get(User, payment_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    payment_data = payment_in.model_dump()
    payment = await crud_payment.create(db, obj_in=payment_data)
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def read_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить платеж по ID.
    """
    payment = await crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден",
        )
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
    payment_in: PaymentUpdate,
):
    """
    Обновить данные платежа.
    """
    payment = await crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден",
        )
    update_data = payment_in.model_dump(exclude_unset=True)
    payment = await crud_payment.update(db, db_obj=payment, obj_in=update_data)
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
):
    """
    Удалить платеж.
    """
    payment = await crud_payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден",
        )
    await crud_payment.delete(db, id=payment_id)
    return None