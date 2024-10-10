# 시험 일정 예약 시스템

## 1. GitHub Repository 링크

[시험 일정 예약 시스템 GitHub Repository](https://github.com/dong-park/grepp-backend)

## 2. 로컬 환경에서 실행하기 위한 환경 설정 및 실행 방법

### 필요 조건

- Docker
- Docker Compose

### 실행 방법

1. 프로젝트 클론:
   ```
   git clone https://github.com/dong-park/grepp-backend.git
   cd grepp-backend
   ```

2. Docker Compose로 서비스 실행:
   ```
   docker-compose up --build
   ```

3. 서비스 접근:
    - API: `http://localhost`

## 3. API 문서

API 문서는 Swagger UI를 통해 제공됩니다. 서비스 실행 후 다음 URL에서 확인할 수 있습니다:

`http://localhost/docs`

## 4. OAuth2PasswordBearer를 이용한 로그인 방법 (form-data 형식)

이 시스템은 OAuth2PasswordBearer를 사용하여 사용자 인증을 처리하며, form-data 형식으로 로그인 요청을 받습니다. 다음은 로그인 과정에 대한 자세한 설명입니다:
API 문서 상단에 Authorize 버튼을 이용하시면 더욱 쉽게 접근 가능합니다.

1. 로그인 요청:
    - 엔드포인트: POST `/v1/users/login`
    - Content-Type: `application/x-www-form-urlencoded`
    - form-data 형식으로 다음 정보를 전송:
      ```
      username: 사용자이름
      password: 비밀번호
      ```

2. 토큰 발급:
    - 로그인 성공 시, 서버는 액세스 토큰을 반환합니다.
    - 응답 예시:
      ```json
      {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
      }
      ```

3. 토큰 사용:
    - 발급받은 토큰을 이용해 인증이 필요한 API에 접근합니다.
    - 요청 헤더에 다음과 같이 토큰을 포함시킵니다:
      ```
      Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      ```

4. 토큰 갱신:
    - 토큰 만료 시 재로그인하여 새 토큰을 발급받아야 합니다.

### 주요 엔드포인트

1. 사용자 관리
    - POST `/v1/users`: 새 사용자 생성
    - POST `/v1/users/login`: 사용자 로그인
    - GET `/v1/users/me`: 현재 사용자 정보 조회

2. 예약 관리
    - GET `/v1/reservations/available-times`: 이용 가능한 시간 조회
    - POST `/v1/reservations`: 새 예약 생성
    - GET `/v1/reservations`: 사용자의 모든 예약 조회
    - GET `/v1/reservations/{reservation_id}`: 특정 예약 조회
    - PUT `/v1/reservations/{reservation_id}`: 예약 수정
    - DELETE `/v1/reservations/{reservation_id}`: 예약 삭제
