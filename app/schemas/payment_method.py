import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PaymentMethodBase(BaseModel):
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    provider: str = Field(..., max_length=50, description="Провайдер: YooKassa, Sberbank, etc.")
    masked_pan: str = Field(..., max_length=20, description="Маскированный номер карты")
    token: Optional[str] = Field(None, max_length=255, description="Токен для повторного использования")
    is_verified: bool = Field(default=False, description="Верифицирован ли способ оплаты")


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    provider: Optional[str] = Field(None, max_length=50)
    masked_pan: Optional[str] = Field(None, max_length=20)
    token: Optional[str] = Field(None, max_length=255)
    is_verified: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True