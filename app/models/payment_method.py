import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # YooKassa, Sberbank, etc.
    masked_pan = Column(String(20), nullable=False)  # маскированный номер карты
    token = Column(String(255), nullable=True)  # токен для повторного использования
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = relationship("User", backref="payment_methods")

    def __repr__(self) -> str:
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, provider={self.provider})>"