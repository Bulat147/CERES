from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CRUDBase
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.auth.security import hash_password

router = APIRouter()

crud_user = CRUDBase(User)


@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список пользователей.
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
):
    """
    Создать нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким телефоном
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.phone == user_in.phone))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже существует",
        )
    user_data = user_in.model_dump()
    user_data["password_hash"] = hash_password(user_data.pop("password"))
    user = await crud_user.create(db, obj_in=user_data)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить пользователя по ID.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
    user_in: UserUpdate,
):
    """
    Обновить данные пользователя.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    update_data = user_in.model_dump(exclude_unset=True)
    user = await crud_user.update(db, db_obj=user, obj_in=update_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
):
    """
    Удалить пользователя.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    await crud_user.delete(db, id=user_id)
    return None