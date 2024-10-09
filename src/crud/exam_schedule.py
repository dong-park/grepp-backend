from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.models import ExamSchedule, Reservation
from src.schemas.reservation import AvailableTimeSchema


def get_exam_schedule(db: Session, exam_id: int):
    return db.query(ExamSchedule).filter(ExamSchedule.exam_id == exam_id).first()


def get_exam_schedule_with_available_capacity(db: Session, exam_id: int):
    result = db.query(
        ExamSchedule.exam_id,
        ExamSchedule.start_time,
        ExamSchedule.max_capacity,
        func.coalesce(func.sum(Reservation.num_participants), 0).label('reserved_participants')
    ).outerjoin(
        Reservation,
        and_(
            Reservation.exam_id == ExamSchedule.exam_id,
            Reservation.is_confirmed is True
        )
    ).filter(
        ExamSchedule.exam_id == exam_id
    ).group_by(
        ExamSchedule.exam_id
    ).having(
        func.coalesce(func.sum(Reservation.num_participants), 0) < ExamSchedule.max_capacity
    ).first()

    return AvailableTimeSchema(
        exam_id=result.exam_id,
        start_time=result.start_time,
        max_capacity=result.max_capacity,
        reserved_participants=result.reserved_participants,
        available_slots=result.max_capacity - result.reserved_participants,
    )
