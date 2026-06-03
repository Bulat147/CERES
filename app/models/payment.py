import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base, GUID


class Payment(Base):
    __tablename__ = "payments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    rental_id = Column(GUID, ForeignKey("rentals.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="RUB")
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, PAID, FAILED, DEBT
    provider = Column(String(50), nullable=True)  # YooKassa, Sberbank, etc.
    provider_payment_id = Column(String(255), nullable=True)  # идентификатор в системе провайдера
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    rental = relationship("Rental", backref="payments")
    user = relationship("User", backref="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, rental_id={self.rental_id}, amount={self.amount})>"