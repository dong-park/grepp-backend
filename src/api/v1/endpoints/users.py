from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_user
from src.schemas.user import User, UserCreate, UserLoginResponse
from src.services import user as user_service

router = APIRouter()


@router.post("",  status_code=status.HTTP_201_CREATED,
             summary="새 사용자 생성",
             description="새로운 사용자를 생성합니다. 이메일이 이미 등록되어 있으면 오류를 반환합니다.")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새 사용자를 생성합니다:
    - **email**: 사용자의 이메일 주소 (중복 불가)
    - **username**: 사용자 이름
    - **password**: 사용자 비밀번호
    """
    user_service.create_user(db=db, request=user)


@router.post("/login", response_model=UserLoginResponse,
             summary="사용자 로그인",
             description="사용자 이름과 비밀번호로 로그인하고 액세스 토큰을 반환합니다.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    사용자 로그인:
    - **username**: 사용자 이름
    - **password**: 사용자 비밀번호
    """
    access_token = user_service.login(db, form_data)
    return UserLoginResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User,
            summary="현재 사용자 정보 조회",
            description="현재 로그인한 사용자의 정보를 반환합니다.")
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자의 정보를 반환합니다.
    """
    return current_user
