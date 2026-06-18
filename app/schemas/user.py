import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    phone: str = Field(..., min_length=5, max_length=20, description="Номер телефона")
    email: Optional[EmailStr] = None
    full_name: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="active", description="active | blocked")


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    password: Optional[str] = Field(None, min_length=4)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True