import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field


class LockerStationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Название постомата")
    address: str = Field(..., min_length=1, max_length=500, description="Адрес")
    latitude: Decimal = Field(..., ge=-90, le=90, description="Широта")
    longitude: Decimal = Field(..., ge=-180, le=180, description="Долгота")
    status: str = Field(default="ACTIVE", description="Статус: ACTIVE, OFFLINE, MAINTENANCE")


class LockerStationCreate(LockerStationBase):
    pass


class LockerStationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    status: Optional[str] = Field(None, description="Статус: ACTIVE, OFFLINE, MAINTENANCE")


class LockerStationResponse(LockerStationBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True