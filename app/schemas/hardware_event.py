import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class HardwareEventBase(BaseModel):
    cell_id: uuid.UUID = Field(..., description="ID ячейки")
    event_type: str = Field(..., max_length=100, description="Тип события: door_opened, door_closed, sensor_error, etc.")
    raw_payload: Optional[Dict[str, Any]] = Field(None, description="Сырые данные от устройства в формате JSON")
    processed: bool = Field(default=False, description="Обработано ли событие системой")


class HardwareEventCreate(HardwareEventBase):
    pass


class HardwareEventResponse(HardwareEventBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True