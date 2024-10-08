from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.api.deps import get_db, get_current_user
from src.schemas.reservation import ReservationCreate, ReservationUpdate, Reservation
from src.services.reservation import ReservationService
from src.models.user import User

router = APIRouter()


@router.post("", response_model=Reservation, summary="새 예약 생성", description="새로운 예약을 생성합니다. 사용자는 반드시 인증되어야 하며, 예약 정보를 제공해야 합니다.")
def create_reservation(
        reservation: ReservationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.create_reservation(db, reservation, current_user.user_id)
    if db_reservation is None:
        raise HTTPException(status_code=400, detail="예약 생성에 실패했습니다. 입력한 정보를 확인해주세요.")
    return db_reservation


@router.get("/{reservation_id}", response_model=Reservation, summary="특정 예약 조회", description="특정 예약의 상세 정보를 조회합니다. 사용자는 자신의 예약만 조회할 수 있습니다.")
def read_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
    if db_reservation.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="이 예약에 접근할 권한이 없습니다. 본인의 예약만 조회할 수 있습니다.")
    return db_reservation


@router.get("", response_model=List[Reservation], summary="사용자의 모든 예약 조회", description="현재 사용자의 모든 예약을 조회합니다. 페이지네이션을 지원합니다.")
def read_user_reservations(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    reservations = ReservationService.get_user_reservations(db, current_user.user_id, skip, limit)
    return reservations


@router.put("/{reservation_id}", response_model=Reservation, summary="예약 수정", description="특정 예약의 정보를 수정합니다. 사용자는 자신의 예약만 수정할 수 있습니다.")
def update_reservation(
        reservation_id: int,
        reservation: ReservationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
    if db_reservation.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="이 예약을 수정할 권한이 없습니다. 본인의 예약만 수정할 수 있습니다.")
    updated_reservation = ReservationService.update_reservation(db, reservation_id, reservation)
    if updated_reservation is None:
        raise HTTPException(status_code=400, detail="예약 업데이트에 실패했습니다. 입력한 정보를 확인해주세요.")
    return updated_reservation


@router.delete("/{reservation_id}", response_model=bool, summary="예약 삭제", description="특정 예약을 삭제합니다. 사용자는 자신의 예약만 삭제할 수 있습니다.")
def delete_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_reservation = ReservationService.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다. 예약 ID를 확인해주세요.")
    if db_reservation.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="이 예약을 삭제할 권한이 없습니다. 본인의 예약만 삭제할 수 있습니다.")
    success = ReservationService.delete_reservation(db, reservation_id)
    if not success:
        raise HTTPException(status_code=400, detail="예약 삭제에 실패했습니다. 다시 시도해주세요.")
    return success
