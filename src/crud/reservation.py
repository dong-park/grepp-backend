# src/crud/reservation.py
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import User
from src.models.reservation import Reservation
from src.schemas.reservation import ReservationCreate, ReservationUpdate


def get_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
    return db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()


def get_reservations(db: Session, skip: int = 0, limit: int = 100) -> List[Reservation]:
    return db.query(Reservation).offset(skip).limit(limit).all()


def get_user_reservations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Reservation]:
    query = db.query(
        Reservation.reservation_id,
        Reservation.exam_id,
        Reservation.is_confirmed,
        Reservation.num_participants,
    )

    if user_id is not None:
        query = query.filter(Reservation.user_id == user_id)

    if user_id is None:
        query = query.join(User, Reservation.user_id == User.user_id)
        query = query.add_columns(
            User.user_id,
            User.username,
            User.email
        )

    query_result = query.offset(skip).limit(limit).all()
    return query_result


def create_reservation(db: Session, reservation: ReservationCreate, user_id: int) -> Optional[Reservation]:
    try:
        db_reservation = Reservation(**reservation.dict(), user_id=user_id)
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    except SQLAlchemyError:
        db.rollback()
        return None


def update_reservation(db: Session, reservation_id: int, request: ReservationUpdate) -> Optional[Reservation]:
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        try:
            update_data = request.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reservation, key, value)
            db.commit()
            db.refresh(db_reservation)
            return db_reservation
        except SQLAlchemyError:
            db.rollback()
    return None


def delete_reservation(db: Session, reservation_id: int) -> bool:
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        try:
            db.delete(db_reservation)
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
    return False


def get_user_reservation(db, exam_id, user_id):
    return db.query(Reservation.reservation_id).filter(
        (Reservation.exam_id == exam_id) & (Reservation.user_id == user_id)).first();
