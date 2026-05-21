import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class CellEventBase(BaseModel):
    cell_id: uuid.UUID = Field(..., description="ID ячейки")
    rental_id: Optional[uuid.UUID] = Field(None, description="ID аренды")
    event_type: str = Field(..., max_length=100, description="Тип события: cell_opened, cell_closed, status_changed, etc.")
    payload_json: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные в формате JSON")


class CellEventCreate(CellEventBase):
    pass


class CellEventResponse(CellEventBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True