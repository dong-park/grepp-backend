from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.user import UserBase


class ReservationBase(BaseModel):
    num_participants: int = Field(..., gt=0)


class ReservationCreate(ReservationBase):
    exam_id: int


class ReservationUpdate(BaseModel):
    num_participants: Optional[int] = Field(None, gt=0)
    is_confirmed: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "num_participants": 6,
                "is_confirmed": True
            }
        }


class ReservationRead(BaseModel):
    reservation_id: int
    exam_id: int
    is_confirmed: bool
    num_participants: int


class UserReservationRead(ReservationRead):
    class Config:
        from_attributes = True


class AdminReservationRead(ReservationRead):
    user: UserBase

    class Config:
        from_attributes = True


class ReservationInDB(ReservationBase):
    reservation_id: int
    user_id: int
    is_confirmed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reservation_id": 1,
                "user_id": 123,
                "start_date": "2023-06-15T14:30:00Z",
                "num_participants": 5,
                "is_confirmed": False,
                "created_at": "2023-06-10T09:00:00Z",
                "updated_at": "2023-06-11T10:30:00Z"
            }
        }


class Reservation(ReservationInDB):
    pass


class AvailableTimeSchema(BaseModel):
    exam_id: int
    start_time: datetime
    max_capacity: int
    reserved_participants: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "exam_id": 1,
                "start_time": "2023-06-15T14:30:00Z",
                "max_capacity": 10,
                "reserved_participants": 5
            }
        }
