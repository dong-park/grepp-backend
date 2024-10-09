from datetime import datetime

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.models import ExamSchedule, Reservation
from src.schemas.reservation import AvailableTimeSchema


def get_available_times(db: Session, start_date: datetime, end_date: datetime):
    query_result = db.query(
        ExamSchedule.exam_id,
        ExamSchedule.start_time,
        ExamSchedule.max_capacity,
        func.coalesce(func.sum(Reservation.num_participants), 0).label('reserved_participants')
    ).outerjoin(
        Reservation,
        and_(
            Reservation.exam_id == ExamSchedule.exam_id,
            Reservation.is_confirmed == True
        )
    ).filter(
        ExamSchedule.start_time > start_date,
        ExamSchedule.start_time <= end_date
    ).group_by(
        ExamSchedule.exam_id
    ).having(
        func.coalesce(func.sum(Reservation.num_participants), 0) < ExamSchedule.max_capacity
    ).all()

    return [AvailableTimeSchema(
        exam_id=result.exam_id,
        start_time=result.start_time,
        max_capacity=result.max_capacity,
        reserved_participants=result.reserved_participants
    ) for result in query_result]
