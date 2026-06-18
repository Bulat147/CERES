import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RentalBase(BaseModel):
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    cell_id: uuid.UUID = Field(..., description="ID ячейки")
    price_per_hour: float = Field(..., ge=0, description="Цена за час")
    status: str = Field(default="CREATED", description="Статус: CREATED, ACTIVE, WAITING_CLOSE, PAYMENT, COMPLETED, CANCELLED, OVERDUE")
    payment_status: str = Field(default="PENDING", description="Статус оплаты: PENDING, PAID, FAILED, DEBT")
    payment_method_id: Optional[uuid.UUID] = Field(None, description="ID способа оплаты")


class RentalCreate(RentalBase):
    pass


class RentalUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    final_amount: Optional[float] = Field(None, ge=0)
    payment_method_id: Optional[uuid.UUID] = None
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class RentalResponse(RentalBase):
    id: uuid.UUID
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    final_amount: Optional[float]
    opened_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
