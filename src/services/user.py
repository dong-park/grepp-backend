from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserUpdate
from src.core.security import create_access_token, get_password_hash, verify_password


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, request: UserCreate):
    if get_user_by_username(db, username=request.username):
        raise HTTPException(status_code=400, detail="이미 등록된 아이디입니다.")

    if get_user_by_email(db, email=request.email):
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")


    hashed_password = get_password_hash(request.password)
    db_user = User(email=request.email, username=request.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def login(db: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = get_user_by_username(db, form_data.username)
    if db_user is None:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    access_token = create_access_token(db_user.username,
                                       expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return access_token
