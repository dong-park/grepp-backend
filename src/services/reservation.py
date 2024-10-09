from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.crud import reservation as reservation_crud, reservation_query
from src.crud import exam_schedule as exam_schedule_crud
from src.models import User
from src.models.reservation import Reservation
from src.schemas.reservation import ReservationCreate, ReservationUpdate, \
    AdminReservationRead, UserReservationRead, ReservationRead
from src.schemas.user import UserBase
from src.utils.time_utils import get_utc_now


class ReservationService:

    @staticmethod
    def create_reservation(db: Session, request: ReservationCreate, user_id: int) -> Optional[Reservation]:
        exam_id = request.exam_id

        # 중복 신청여부 확인
        reservation = reservation_crud.get_user_reservation(db, exam_id, user_id)
        if reservation is not None:
            raise HTTPException(status_code=400, detail="이미 존재하는 예약이 있습니다.")

        # 예약 가능 여부 확인 (3일전, 최대 5만명)
        exam_schedule = exam_schedule_crud.get_exam_schedule_with_available_capacity(db, exam_id)
        now = get_utc_now()
        three_days_later = now + timedelta(days=3)
        if exam_schedule is None:
            raise HTTPException(status_code=400, detail="예약이 가능하지 않은 날짜입니다.")

        if exam_schedule.reserved_participants + request.num_participants > exam_schedule.max_capacity:
            raise HTTPException(status_code=400, detail="예약 가능한 인원을 초과했습니다.")

        if exam_schedule.start_time < now:
            raise HTTPException(status_code=400, detail="예약이 가능하지 않은 날짜입니다.")

        if exam_schedule.start_time > three_days_later:
            raise HTTPException(status_code=400, detail="예약이 가능하지 않은 날짜입니다.")

        # 임시 예약 저장
        return reservation_crud.create_reservation(db, request, user_id)

    @staticmethod
    def get_reservation(db: Session, reservation_id: int, current_user: User) -> Optional[Reservation]:
        db_reservation = reservation_crud.get_reservation(db, reservation_id)
        if db_reservation is None:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
        if not current_user.is_admin and db_reservation.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="이 예약에 접근할 권한이 없습니다. 본인의 예약만 조회할 수 있습니다.")
        return db_reservation

    @staticmethod
    def get_user_reservations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ReservationRead]:
        query_results = reservation_crud.get_user_reservations(db, user_id, skip, limit)

        if user_id is not None:
            return [UserReservationRead.from_orm(result) for result in query_results]
        else:
            return [AdminReservationRead(
                reservation_id=result.reservation_id,
                exam_id=result.exam_id,
                is_confirmed=result.is_confirmed,
                num_participants=result.num_participants,
                user=UserBase(
                    user_id=result.user_id,
                    email=result.email,
                    username=result.username
                )
            ) for result in query_results]

    @staticmethod
    def update_reservation(db: Session, reservation_id: int, request: ReservationUpdate, current_user: User) -> \
    Optional[Reservation]:
        db_reservation = reservation_crud.get_reservation(db, reservation_id)
        if db_reservation is None:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
        if not current_user.is_admin and db_reservation.user_id != current_user.user_id:
            raise HTTPException(status_code=400, detail="해당 예약에 대한 수정 권한이 없습니다.")
        if not current_user.is_admin and request.is_confirmed is not None:
            raise HTTPException(status_code=400, detail="해당 예약에 대한 허가 권한이 없습니다.")

        return reservation_crud.update_reservation(db, reservation_id, request)

    @staticmethod
    def delete_reservation(db: Session, reservation_id: int, current_user: User) -> bool:
        db_reservation = ReservationService.get_reservation(db, reservation_id, current_user)
        if db_reservation is None:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
        if not current_user.is_admin and db_reservation.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="이 예약을 삭제할 권한이 없습니다. 본인의 예약만 삭제할 수 있습니다.")
        return reservation_crud.delete_reservation(db, reservation_id)

    @staticmethod
    def get_available_times(db: Session):
        now = datetime.now()
        three_days_later = now + timedelta(days=3)

        available_times = reservation_query.get_available_times(db, now, three_days_later)
        return available_times
