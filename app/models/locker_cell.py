import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class LockerCell(Base):
    __tablename__ = "locker_cells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("locker_stations.id"), nullable=False)
    number = Column(Integer, nullable=False)  # номер ячейки в постомате
    size = Column(String(20), nullable=False)  # SMALL, MEDIUM, LARGE
    hourly_price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default="AVAILABLE")  # AVAILABLE, RESERVED, ACTIVE, PAYMENT, BLOCKED, OFFLINE
    hardware_id = Column(String(100), nullable=True)  # идентификатор физического устройства
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    station = relationship("LockerStation", backref="cells")

    def __repr__(self) -> str:
        return f"<LockerCell(id={self.id}, station_id={self.station_id}, status={self.status})>"