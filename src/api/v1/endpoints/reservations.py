from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_user
from src.models.user import User
from src.schemas.reservation import ReservationCreate, ReservationUpdate, Reservation, UserReservationRead, \
    AdminReservationRead, ReservationRead
from src.services.reservation import ReservationService

router = APIRouter()


@router.get("/available-times")
def available_times(
        db: Session = Depends(get_db),
):
    times = ReservationService.get_available_times(db)
    return times


@router.post("", response_model=Reservation, summary="새 예약 생성",
             description="새로운 예약을 생성합니다. 사용자는 반드시 인증되어야 하며, 예약 정보를 제공해야 합니다.", status_code=status.HTTP_201_CREATED)
def create_reservation(
        reservation: ReservationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.create_reservation(db, reservation, current_user.user_id)
    if db_reservation is None:
        raise HTTPException(status_code=400, detail="예약 생성에 실패했습니다. 입력한 정보를 확인해주세요.")
    return db_reservation


@router.get("", response_model=Union[List[UserReservationRead], List[AdminReservationRead]], summary="사용자의 모든 예약 조회",
            description="현재 사용자의 모든 예약을 조회합니다. 페이지네이션을 지원합니다.", status_code=status.HTTP_200_OK)
def read_user_reservations(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    is_admin = current_user.is_admin
    reservations = ReservationService.get_user_reservations(
        db, None if is_admin else current_user.user_id, skip, limit)
    return reservations


@router.get("/{reservation_id}", summary="특정 예약 조회",
            description="특정 예약의 상세 정보를 조회합니다. 사용자는 자신의 예약만 조회할 수 있습니다.", status_code=status.HTTP_200_OK)
def read_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.get_reservation(db, reservation_id, current_user)
    return db_reservation


@router.put("/{reservation_id}", summary="예약 수정",
            description="특정 예약의 정보를 수정합니다. 사용자는 자신의 예약만 수정할 수 있습니다.", status_code=status.HTTP_200_OK)
def update_reservation(
        reservation_id: int,
        request: ReservationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    updated_reservation = ReservationService.update_reservation(db, reservation_id, request, current_user)
    if updated_reservation is None:
        raise HTTPException(status_code=400, detail="예약 업데이트에 실패했습니다. 입력한 정보를 확인해주세요.")


@router.delete("/{reservation_id}", summary="예약 삭제",
               description="특정 예약을 삭제합니다. 사용자는 자신의 예약만 삭제할 수 있습니다.", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    success = ReservationService.delete_reservation(db, reservation_id, current_user)
    if not success:
        raise HTTPException(status_code=400, detail="예약 삭제에 실패했습니다. 다시 시도해주세요.")
