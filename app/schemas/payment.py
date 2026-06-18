import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    rental_id: uuid.UUID = Field(..., description="ID аренды")
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    payment_method_id: Optional[uuid.UUID] = Field(None, description="ID способа оплаты")
    amount: float = Field(..., ge=0, description="Сумма платежа")
    currency: str = Field(default="RUB", max_length=3, description="Валюта")
    status: str = Field(default="PENDING", description="Статус: PENDING, PAID, FAILED, DEBT")
    provider: Optional[str] = Field(None, max_length=50, description="Провайдер платежа")
    provider_payment_id: Optional[str] = Field(None, max_length=255, description="ID платежа у провайдера")


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=50)
    provider_payment_id: Optional[str] = Field(None, max_length=255)
    payment_method_id: Optional[uuid.UUID] = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
