from typing import Optional

from pydantic import BaseModel, EmailStr, Field

password_field = Field(
    ...,
    min_length=8,
    max_length=30,
    pattern=r"^[A-Za-z\d@$!%*?&#]+$",
    description="사용자의 비밀번호",
    example="Password123!@#",
    error_messages={
        "min_length": "비밀번호는 최소 8자 이상이어야 합니다.",
        "max_length": "비밀번호는 최대 30자를 초과할 수 없습니다.",
        "pattern": "비밀번호는 8~30자 사이여야 하며, 대문자, 소문자, 숫자, 특수문자(@$!%*?&#)를 각각 하나 이상 포함해야 합니다."
    }
)


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="사용자의 이메일 주소", example="grepp@example.com")
    username: str = Field(..., description="사용자의 이름", example="grepp")


class UserCreate(UserBase):
    password: str = password_field

    class Config:
        json_schema_extra = {
            "example": {
                "email": "grepp@example.com",
                "username": "grepp",
                "password": "password123!@#"
            }
        }


class UserLogin(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="사용자의 이름",
        example="grepp",
        error_messages={
            "min_length": "사용자 이름은 최소 3자 이상이어야 합니다.",
            "max_length": "사용자 이름은 최대 20자를 초과할 수 없습니다."
        }
    )
    password: str = password_field

    class Config:
        json_schema_extra = {
            "example": {
                "username": "grepp",
                "password": "Password123!@#"
            }
        }


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="업데이트할 이메일 주소")
    username: Optional[str] = Field(None, description="업데이트할 사용자 이름")
    password: Optional[str] = Field(None, description="업데이트할 비밀번호")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "updated@example.com",
                "username": "업데이트된사용자",
                "password": "새로운비밀번호456!"
            }
        }


class UserInDB(UserBase):
    user_id: int = Field(..., description="사용자의 고유 식별자")
    hashed_password: str = Field(..., description="해시된 비밀번호")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "데이터베이스사용자",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            }
        }


class UserRead(UserBase):
    pass


class User(UserBase):
    user_id: int = Field(..., description="사용자의 고유 식별자")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "사용자이름",
                "id": 1
            }
        }


class UserLoginResponse(BaseModel):
    access_token: str = Field(..., description="액세스 토큰",
                              example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImlhdCI6MTUxNjIzOTAyMn0.Q23Qk5z5Y4_y5Xx_5xYw50W3YR68Y4Y")
    token_type: str = Field(..., description="토큰 타입", example="bearer")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImlhdCI6MTUxNjIzOTAyMn0.Q23Qk5z5Y4_y5Xx_5xYw50W3YR68Y4Y",
                "token_type": "bearer"
            }
        }
