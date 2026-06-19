from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.deps import get_current_user
from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.payment_method import PaymentMethod
from app.models.user import User
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse

router = APIRouter()

crud_payment_method = CRUDBase(PaymentMethod)


@router.get("/", response_model=List[PaymentMethodResponse], dependencies=[Depends(get_current_user)])
async def read_payment_methods(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: UUID = None,
):
    """
    Получить список способов оплаты.
    Можно отфильтровать по user_id.
    """
    query = select(PaymentMethod)
    if user_id:
        query = query.where(PaymentMethod.user_id == user_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    methods = result.scalars().all()
    return methods


@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_payment_method(
    *,
    db: AsyncSession = Depends(get_db),
    method_in: PaymentMethodCreate,
):
    """
    Создать новый способ оплаты.
    """
    # Проверяем существование пользователя
    user = await db.get(User, method_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    method_data = method_in.model_dump()
    method = await crud_payment_method.create(db, obj_in=method_data)
    return method


@router.get("/{method_id}", response_model=PaymentMethodResponse, dependencies=[Depends(get_current_user)])
async def read_payment_method(
    method_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить способ оплаты по ID.
    """
    method = await crud_payment_method.get(db, id=method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Способ оплаты не найден",
        )
    return method


@router.put("/{method_id}", response_model=PaymentMethodResponse, dependencies=[Depends(get_current_user)])
async def update_payment_method(
    *,
    db: AsyncSession = Depends(get_db),
    method_id: UUID,
    method_in: PaymentMethodUpdate,
):
    """
    Обновить данные способа оплаты.
    """
    method = await crud_payment_method.get(db, id=method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Способ оплаты не найден",
        )
    update_data = method_in.model_dump(exclude_unset=True)
    method = await crud_payment_method.update(db, db_obj=method, obj_in=update_data)
    return method


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def delete_payment_method(
    *,
    db: AsyncSession = Depends(get_db),
    method_id: UUID,
):
    """
    Удалить способ оплаты.
    """
    method = await crud_payment_method.get(db, id=method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Способ оплаты не найден",
        )
    await crud_payment_method.delete(db, id=method_id)
    return None