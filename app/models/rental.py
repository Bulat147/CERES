import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base, GUID


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    cell_id = Column(GUID, ForeignKey("locker_cells.id"), nullable=False)
    started_at = Column(DateTime, nullable=True)  # когда ячейка была открыта
    ended_at = Column(DateTime, nullable=True)  # когда аренда завершена (после оплаты)
    status = Column(String(50), nullable=False, default="CREATED")  # CREATED, ACTIVE, WAITING_CLOSE, PAYMENT, COMPLETED, CANCELLED, OVERDUE
    price_per_hour = Column(DECIMAL(10, 2), nullable=False)
    final_amount = Column(DECIMAL(10, 2), nullable=True)  # итоговая сумма к оплате
    payment_status = Column(String(20), nullable=False, default="PENDING")  # PENDING, PAID, FAILED, DEBT
    payment_method_id = Column(GUID, ForeignKey("payment_methods.id"), nullable=True)  # способ оплаты
    opened_at = Column(DateTime, nullable=True)  # когда ячейка была открыта пользователем
    closed_at = Column(DateTime, nullable=True)  # когда пользователь физически закрыл дверь
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = relationship("User", backref="rentals")
    cell = relationship("LockerCell", backref="rentals")

    def __repr__(self) -> str:
        return f"<Rental(id={self.id}, user_id={self.user_id}, status={self.status})>"