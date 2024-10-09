# src/crud/reservation_crud.py
from typing import Optional

from sqlalchemy.orm import Session

from src.models.reservation import Reservation
from src.schemas.reservation import ReservationCreate, ReservationUpdate


def get_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
    return db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()


def get_user_reservation(db, exam_id, user_id):
    return db.query(Reservation.reservation_id).filter(
        (Reservation.exam_id == exam_id) & (Reservation.user_id == user_id)).first()


def create_reservation(db: Session, reservation: ReservationCreate, user_id: int) -> Optional[Reservation]:
    db_reservation = Reservation(**reservation.dict(), user_id=user_id)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def update_reservation(db: Session, reservation_id: int, request: ReservationUpdate) -> Optional[Reservation]:
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        update_data = request.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_reservation, key, value)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    return None


def delete_reservation(db: Session, reservation_id: int) -> bool:
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        db.delete(db_reservation)
        db.commit()
        return True
    return False
