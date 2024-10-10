import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.security import get_password_hash
from src.models import User, ExamSchedule, Reservation

# 데이터베이스 연결 설정
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake = Faker('ko_KR')  # 한국어 데이터 생성

def create_fake_users(num_users=10):
    users = []
    for _ in range(num_users):
        user = User(
            email=fake.email(),
            username=fake.user_name() if len(fake.user_name()) >= 4 else fake.user_name() + fake.lexify(text='?' * (4 - len(fake.user_name()))),
            hashed_password=get_password_hash(fake.password()),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_active=True,
            is_admin=random.choice([True, False])
        )
        users.append(user)
    return users

def create_fake_exam_schedules(num_schedules=20):
    schedules = []
    start_date = datetime.now() + timedelta(days=1)
    for _ in range(num_schedules):
        start_time = start_date + timedelta(days=random.randint(0, 30))
        start_time = start_time.replace(hour=random.randint(12, 22), minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=random.choice([1, 2]))
        schedule = ExamSchedule(
            start_time=start_time,
            name=fake.sentence(nb_words=3, variable_nb_words=True),
            end_time=end_time,
            max_capacity=random.randint(20, 49) * 1000
        )
        schedules.append(schedule)
    return schedules

def create_fake_reservations(users, exam_schedules, num_reservations=200):
    reservations = []
    for _ in range(num_reservations):
        user = random.choice(users)
        exam_schedule = random.choice(exam_schedules)
        reservation = Reservation(
            user_id=user.user_id,
            exam_id=exam_schedule.exam_id,
            num_participants=random.randint(1, 10) * 1000,
            is_confirmed=random.choice([True, False])
        )
        reservations.append(reservation)
    return reservations

def main():
    db = SessionLocal()
    try:
        # 가짜 사용자 생성
        users = create_fake_users()
        db.add_all(users)
        db.commit()

        # 가짜 시험 일정 생성
        exam_schedules = create_fake_exam_schedules()
        db.add_all(exam_schedules)
        db.commit()

        # 가짜 예약 생성
        reservations = create_fake_reservations(users, exam_schedules)
        db.add_all(reservations)
        db.commit()

        print("가짜 데이터가 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"데이터 생성 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
