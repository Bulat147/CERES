import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class HardwareEvent(Base):
    __tablename__ = "hardware_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id = Column(UUID(as_uuid=True), ForeignKey("locker_cells.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # door_opened, door_closed, sensor_error, etc.
    raw_payload = Column(JSON, nullable=True)  # сырые данные от устройства
    processed = Column(Boolean, default=False, nullable=False)  # обработано ли событие системой
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    cell = relationship("LockerCell", backref="hardware_events")

    def __repr__(self) -> str:
        return f"<HardwareEvent(id={self.id}, cell_id={self.cell_id}, event_type={self.event_type})>"