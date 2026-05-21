import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class CellEvent(Base):
    __tablename__ = "cell_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id = Column(UUID(as_uuid=True), ForeignKey("locker_cells.id"), nullable=False)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # cell_opened, cell_closed, status_changed, etc.
    payload_json = Column(JSON, nullable=True)  # дополнительные данные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    cell = relationship("LockerCell", backref="events")
    rental = relationship("Rental", backref="events")

    def __repr__(self) -> str:
        return f"<CellEvent(id={self.id}, cell_id={self.cell_id}, event_type={self.event_type})>"