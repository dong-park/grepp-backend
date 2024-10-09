from sqlalchemy import Column, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    exam_id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    max_capacity = Column(Integer, nullable=False, default=50000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    reservations = relationship("Reservation", back_populates="exam_schedule")

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_end_time_after_start_time'),
        CheckConstraint('max_capacity > 0', name='check_positive_max_capacity'),
    )

    def __repr__(self):
        return f"<ExamSchedule {self.id}: {self.start_time} - {self.end_time}>"
