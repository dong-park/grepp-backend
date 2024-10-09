from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.schemas.user import UserBase


class ReservationBase(BaseModel):
    num_participants: int = Field(..., gt=0, description="참가자 수")

    @field_validator('num_participants')
    @classmethod
    def validate_positive_number(cls, v, field):
        if v <= 0:
            raise ValueError(f'{field.name}는 0보다 커야 합니다.')
        return v


class ReservationCreate(ReservationBase):
    exam_id: int = Field(..., gt=0, description="시험 ID")


class ReservationUpdate(BaseModel):
    num_participants: Optional[int] = Field(None, gt=0, description="참가자 수")
    is_confirmed: Optional[bool] = Field(None, description="예약 확정 여부")

    _validate_num_participants = field_validator('num_participants')(ReservationBase.validate_positive_number)

    class Config:
        json_schema_extra = {
            "example": {
                "num_participants": 10000,
                "is_confirmed": True
            }
        }


class ReservationRead(BaseModel):
    reservation_id: int = Field(..., description="예약 ID")
    exam_id: int = Field(..., description="시험 ID")
    is_confirmed: bool = Field(..., description="예약 확정 여부")
    num_participants: int = Field(..., description="참가자 수")


class UserReservationRead(ReservationRead):
    class Config:
        from_attributes = True


class AdminReservationRead(ReservationRead):
    user: UserBase = Field(..., description="사용자 정보")

    class Config:
        from_attributes = True


class ReservationInDB(ReservationBase):
    reservation_id: int = Field(..., description="예약 ID")
    user_id: int = Field(..., gt=0, description="사용자 ID")
    is_confirmed: bool = Field(..., description="예약 확정 여부")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reservation_id": 1,
                "user_id": 123,
                "num_participants": 5,
                "is_confirmed": False,
                "created_at": "2023-06-10T09:00:00Z",
                "updated_at": "2023-06-11T10:30:00Z"
            }
        }


class Reservation(ReservationInDB):
    pass


class AvailableTimeSchema(BaseModel):
    exam_id: int = Field(..., description="시험 ID")
    start_time: datetime = Field(..., description="시험 시작 시간")
    max_capacity: int = Field(..., gt=0, description="최대 수용 인원")
    reserved_participants: int = Field(..., ge=0, description="예약된 참가자 수")
    available_slots: int = Field(..., ge=0, description="예약 가능한 참가자 수")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "exam_id": 1,
                "start_time": "2023-06-15T14:30:00Z",
                "max_capacity": 10,
                "reserved_participants": 5,
                "available_slots": 5
            }
        }
