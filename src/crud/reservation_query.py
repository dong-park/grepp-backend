from datetime import datetime
from typing import List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.models import ExamSchedule, Reservation, User
from src.schemas.reservation import AvailableTimeSchema


def get_user_reservation_join(query, user_id):
    query = query.join(ExamSchedule, Reservation.exam_id == ExamSchedule.exam_id, isouter=True)
    if user_id is not None:
        query = query.filter(Reservation.user_id == user_id)
    if user_id is None:
        query = query.join(User, Reservation.user_id == User.user_id, isouter=True)
        query = query.add_columns(
            User.user_id,
            User.username,
            User.email
        )
    return query


def get_user_reservations(db: Session, user_id: int, page: int = 0, limit: int = 100) -> List[Reservation]:
    query = (db.query(
        Reservation.reservation_id,
        Reservation.exam_id,
        Reservation.is_confirmed,
        Reservation.num_participants,
        ExamSchedule.name.label("exam_name")
    ))

    query = get_user_reservation_join(query, user_id)
    query.order_by(Reservation.reservation_id)
    offset = (page - 1) * limit
    query_result = query.offset(offset).limit(limit).all()
    return query_result


def get_user_reservations_count(db: Session, user_id: int) -> int:
    query = db.query(Reservation.exam_id)
    query = get_user_reservation_join(query, user_id)
    return query.count()


def get_available_times(db: Session, start_date: datetime, end_date: datetime):
    query_result = (db.query(
        ExamSchedule.exam_id,
        ExamSchedule.name,
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
    ).order_by(
        ExamSchedule.start_time
    ).all())

    return [AvailableTimeSchema(
        exam_id=result.exam_id,
        name=result.name,
        start_time=result.start_time,
        max_capacity=result.max_capacity,
        reserved_participants=result.reserved_participants,
        available_capacity=result.max_capacity - result.reserved_participants,
    ) for result in query_result]
