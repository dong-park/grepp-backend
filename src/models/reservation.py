from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base

class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    exam_date = Column(DateTime, nullable=False)
    num_participants = Column(Integer, nullable=False)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="reservations")

    __table_args__ = (
        CheckConstraint('num_participants > 0', name='check_positive_participants'),
    )

    def __repr__(self):
        return f"<Reservation {self.reservation_id}: {self.exam_date}>"
