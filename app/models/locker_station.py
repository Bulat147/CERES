import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class LockerStation(Base):
    __tablename__ = "locker_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, OFFLINE, MAINTENANCE
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<LockerStation(id={self.id}, title={self.title}, status={self.status})>"