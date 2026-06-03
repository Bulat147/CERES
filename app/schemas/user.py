import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Базовые схемы
class UserBase(BaseModel):
    phone: str = Field(..., min_length=5, max_length=20, description="Номер телефона")
    email: Optional[EmailStr] = None
    full_name: str = Field(..., min_length=1, max_length=255, description="Полное имя")
    status: str = Field(default="active", description="Статус пользователя: active, blocked")


# Схема для создания пользователя
class UserCreate(UserBase):
    pass


# Схема для обновления пользователя
class UserUpdate(BaseModel):
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, description="Статус пользователя: active, blocked")


# Схема ответа API
class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True