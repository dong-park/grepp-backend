from datetime import timedelta
from typing import Optional, Union

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.crud import exam_schedule as exam_schedule_crud
from src.crud import reservation_crud as reservation_crud
from src.crud import reservation_query
from src.crud.reservation_query import get_user_reservations_count
from src.models import User
from src.models.reservation import Reservation
from src.schemas.reservation import (AdminReservationRead, ReservationCreate,
                                     ReservationUpdate,
                                     UserReservationRead, UserReservationReadList, AdminReservationReadList)
from src.schemas.user import UserBase
from src.utils.time_utils import get_kst_now


class ReservationService:

    @staticmethod
    def create_reservation(db: Session, request: ReservationCreate, user_id: int) -> Optional[Reservation]:
        exam_id = request.exam_id

        # 중복 신청여부 확인
        reservation = reservation_crud.get_user_reservation(db, exam_id, user_id)
        if reservation is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 예약이 있습니다.")

        # 예약 가능 여부 확인 (3일전, 최대 5만명)
        exam_schedule = exam_schedule_crud.get_exam_schedule_with_available_capacity(db, exam_id)
        now = get_kst_now()
        three_days_later = now + timedelta(days=3)
        if exam_schedule is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약이 가능하지 않은 날짜입니다.")

        if exam_schedule.reserved_participants + request.num_participants > exam_schedule.max_capacity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약 가능한 인원을 초과했습니다.")

        if exam_schedule.start_time < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약이 가능하지 않은 날짜입니다.")

        if exam_schedule.start_time > three_days_later:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약이 가능하지 않은 날짜입니다.")

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
    def get_user_reservations(db: Session, user_id: int, page: int = 1, limit: int = 100) -> Union[
        UserReservationReadList, AdminReservationReadList]:
        total_items = get_user_reservations_count(db, user_id)
        query_results = reservation_query.get_user_reservations(db, user_id, page, limit)
        total_pages = total_items // limit + (1 if total_items % limit > 0 else 0)

        if user_id is not None:
            read_schema = [UserReservationRead.from_orm(result) for result in query_results]
            return UserReservationReadList(
                revations=read_schema,
                page=page,
                page_size=limit,
                total_itmes=total_items,
                total_pages=total_pages
            )
        else:
            read_schema = [AdminReservationRead(
                reservation_id=result.reservation_id,
                exam_id=result.exam_id,
                exam_name=result.exam_name,
                is_confirmed=result.is_confirmed,
                num_participants=result.num_participants,
                user=UserBase(
                    user_id=result.user_id,
                    email=result.email,
                    username=result.username
                )
            ) for result in query_results]
            return AdminReservationReadList(
                revations=read_schema,
                page=page,
                page_size=limit,
                total_itmes=total_items,
                total_pages=total_pages
            )

    @staticmethod
    def update_reservation(db: Session, reservation_id: int, request: ReservationUpdate, current_user: User) -> \
    Optional[
        Reservation]:
        db_reservation = reservation_crud.get_reservation_for_update(db, reservation_id)
        if db_reservation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")

        # 권한 확인
        if not current_user.is_admin and db_reservation.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 예약에 대한 수정 권한이 없습니다.")
        if not current_user.is_admin and request.is_confirmed is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 예약에 대한 허가 권한이 없습니다.")

        # 예약 상태 업데이트
        return reservation_crud.update_reservation(db, reservation_id, request)

    @staticmethod
    def delete_reservation(db: Session, reservation_id: int, current_user: User) -> bool:
        db_reservation = ReservationService.get_reservation(db, reservation_id, current_user)
        if db_reservation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
        if not current_user.is_admin and db_reservation.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 예약을 삭제할 권한이 없습니다. 본인의 예약만 삭제할 수 있습니다.")
        if db_reservation.num_participants > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약 가능 인원을 초과했습니다.")
        return reservation_crud.delete_reservation(db, reservation_id)

    @staticmethod
    def get_available_times(db: Session):
        now = get_kst_now()
        three_days_later = now + timedelta(days=3)

        available_times = reservation_query.get_available_times(db, now, three_days_later)
        return available_times
