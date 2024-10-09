import random
import bcrypt
from faker import Faker
from src.core.config import settings
from tqdm import tqdm
import concurrent.futures
import multiprocessing

# 데이터베이스 연결 설정
DATABASE_URL = settings.DATABASE_URL

fake = Faker('ko_KR')  # 한국어 데이터 생성

def create_user():
    email = fake.email()
    username = fake.unique.user_name()
    while len(username) < 4:
        username = fake.unique.user_name()
    hashed_password = f'{fake.uuid4()}'  # 로그인을 사용하지 않지만 고유한 가짜 데이터 생성
    return f"('{email}', '{username}', '{hashed_password}', '{fake.first_name()}', '{fake.last_name()}', TRUE, {str(random.random() < 0.01).upper()})"

def create_fake_users(num_users: int = 50000, batch_size: int = 1000):
    # SQL 문 준비
    insert_query = """
    INSERT INTO users (email, username, hashed_password, first_name, last_name, is_active, is_admin)
    VALUES
    """

    with open('fake_user.sql', 'w', encoding='utf-8') as f:
        f.write(insert_query)
        total_inserted = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = [executor.submit(create_user) for _ in range(num_users)]

            with tqdm(total=num_users, desc="사용자 데이터 생성 중") as pbar:
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    user = future.result()
                    f.write(user + ",\n")

                    if (i + 1) % batch_size == 0 or i == num_users - 1:
                        f.seek(f.tell() - 2)  # 마지막 쉼표와 줄바꿈 제거
                        f.write(";\n\n")
                        if i != num_users - 1:
                            f.write(insert_query)
                        total_inserted += batch_size if i != num_users - 1 else (i % batch_size) + 1

                    pbar.update(1)

    print(f"총 {total_inserted} 명의 사용자 데이터 SQL 문이 fake_user.sql 파일에 생성되었습니다.")

if __name__ == "__main__":
    create_fake_users()
