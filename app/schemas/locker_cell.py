import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LockerCellBase(BaseModel):
    station_id: uuid.UUID = Field(..., description="ID постомата")
    number: int = Field(..., ge=1, description="Номер ячейки")
    title: str = Field(default="", max_length=255, description="Название ячейки")
    size: str = Field(..., description="Размер: SMALL, MEDIUM, LARGE")
    hourly_price: float = Field(..., ge=0, description="Цена за час")
    status: str = Field(default="AVAILABLE", description="Статус: AVAILABLE, RESERVED, ACTIVE, PAYMENT, BLOCKED, OFFLINE")
    hardware_id: Optional[str] = Field(None, max_length=100, description="Идентификатор физического устройства")


class LockerCellCreate(LockerCellBase):
    pass


class LockerCellUpdate(BaseModel):
    station_id: Optional[uuid.UUID] = None
    number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = None
    hourly_price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    hardware_id: Optional[str] = Field(None, max_length=100)


class LockerCellResponse(LockerCellBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
