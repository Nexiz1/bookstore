# 📚 BookStore API

온라인 서점 백엔드 API - FastAPI + MySQL + Docker Compose

## 📋 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **학번** | 202111666 |
| **작성자** | 최진서 |
| **DBMS** | MySQL 8.0 (MariaDB 호환) |
| **DB Name** | bookStoreDb |
| **API 개수** | 36개 엔드포인트 |
| **Python** | 3.12 |
| **Framework** | FastAPI |

## 🏗️ 아키텍처

```
app/
├── api/                    # Presentation Layer
│   ├── routers/           # 12개 API 라우터
│   │   ├── auth.py        # 인증 (4 endpoints)
│   │   ├── users.py       # 회원 (5 endpoints)
│   │   ├── sellers.py     # 판매자 (3 endpoints)
│   │   ├── books.py       # 도서 (5 endpoints)
│   │   ├── carts.py       # 장바구니 (4 endpoints)
│   │   ├── orders.py      # 주문 (4 endpoints)
│   │   ├── reviews.py     # 리뷰 (3 endpoints)
│   │   ├── favorites.py   # 찜하기 (3 endpoints)
│   │   ├── rankings.py    # 랭킹 (1 endpoint)
│   │   ├── sales.py       # 세일 (2 endpoints)
│   │   ├── settlements.py # 정산 (1 endpoint)
│   │   └── admin.py       # 관리자 (1 endpoint)
│   └── dependencies.py    # 의존성 주입 & JWT 인증
├── services/              # Business Logic Layer (12개)
├── repositories/          # Data Access Layer (11개)
├── models/                # SQLAlchemy ORM Models (13개 테이블)
├── schemas/               # Pydantic DTOs (Request/Response)
├── core/
│   ├── config.py          # 환경 설정
│   ├── database.py        # DB 연결
│   └── security.py        # JWT & 비밀번호 해싱
├── exceptions/            # 커스텀 예외 & 핸들러 (10개 도메인별 예외)
├── middleware/            # 로깅 미들웨어
├── utils/                 # 유틸리티 (로깅 설정)
└── main.py                # Application Entry Point

tests/                     # 테스트 코드
├── conftest.py            # pytest fixtures
├── test_auth.py           # 인증 테스트
├── test_users.py          # 사용자 테스트
├── test_sellers.py        # 판매자 테스트
├── test_books.py          # 도서 테스트
├── test_carts.py          # 장바구니 테스트
├── test_orders.py         # 주문 테스트
├── test_reviews.py        # 리뷰 테스트
└── test_favorites.py      # 찜하기 테스트
```

## 🚀 빠른 시작

### Docker Compose (권장)

```bash
# 1. 환경변수 설정
cp .env.example .env

# 2. 컨테이너 빌드 및 실행
docker-compose up --build

# 3. API 문서 확인
# http://localhost:8000/docs
```

### VS Code DevContainer

1. VS Code에서 프로젝트 열기
2. `F1` → `Dev Containers: Reopen in Container` 선택
3. 자동으로 MySQL + FastAPI 환경 구성

### 로컬 개발 환경

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에서 DATABASE_URL 수정

# 4. 서버 실행
uvicorn app.main:app --reload
```

## 📡 API 엔드포인트 (Total: 36)

### 1. 인증 (Auth) - 4개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/auth/signup` | 회원가입 | Anyone |
| POST | `/auth/login` | 로그인 (JWT 발급) | Anyone |
| POST | `/auth/refresh` | 토큰 재발급 | Anyone |
| POST | `/auth/logout` | 로그아웃 | User/Seller/Admin |

### 2. 회원 (Users) - 5개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/users/me` | 내 프로필 조회 | User/Seller/Admin |
| PATCH | `/users/me` | 내 프로필 수정 | User/Seller/Admin |
| POST | `/users/me/password` | 비밀번호 변경 | User/Seller/Admin |
| GET | `/users` | 전체 회원 목록 | Admin |
| PATCH | `/users/{user_id}/role` | 회원 권한 변경 | Admin |

### 3. 판매자 (Sellers) - 3개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/sellers` | 판매자 등록 신청 | User |
| GET | `/sellers/me` | 내 판매자 정보 조회 | Seller |
| PATCH | `/sellers/me` | 판매자 정보 수정 | Seller |

### 4. 도서 (Books) - 5개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/books` | 도서 등록 | Seller |
| GET | `/books` | 도서 목록 조회 (검색, 정렬, 필터) | Anyone |
| GET | `/books/{book_id}` | 도서 상세 조회 | Anyone |
| PUT | `/books/{book_id}` | 도서 정보 수정 | Seller (본인) |
| DELETE | `/books/{book_id}` | 도서 삭제 (SOLDOUT) | Seller (본인) |

### 5. 장바구니 (Carts) - 4개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/carts` | 내 장바구니 조회 | User |
| POST | `/carts` | 장바구니 담기 | User |
| PATCH | `/carts/{cart_id}` | 수량 변경 | User |
| DELETE | `/carts/{cart_id}` | 장바구니 아이템 삭제 | User |

### 6. 주문 (Orders) - 4개 + Admin 1개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/orders` | 주문 생성 | User |
| GET | `/orders` | 내 주문 내역 조회 | User |
| GET | `/orders/{order_id}` | 주문 상세 조회 | User |
| POST | `/orders/{order_id}/cancel` | 주문 취소 | User |
| GET | `/admin/orders` | 전체 주문 현황 | Admin |

### 7. 리뷰 (Reviews) - 3개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/books/{book_id}/reviews` | 리뷰 작성 | User (구매자) |
| GET | `/books/{book_id}/reviews` | 리뷰 목록 조회 | Anyone |
| DELETE | `/reviews/{review_id}` | 리뷰 삭제 | User (작성자)/Admin |

### 8. 찜하기 (Favorites) - 3개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/books/{book_id}/favorites` | 찜하기 등록 | User |
| DELETE | `/books/{book_id}/favorites` | 찜하기 취소 | User |
| GET | `/favorites` | 내 찜 목록 조회 | User |

### 9. 랭킹 (Rankings) - 1개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/rankings` | 랭킹 조회 (type, ageGroup, gender) | Anyone |

### 10. 세일 & 정산 - 3개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/sales` | 타임 세일 생성 | Seller |
| POST | `/sales/{sale_id}/books` | 세일 도서 추가 | Seller |
| GET | `/settlements` | 정산 내역 조회 | Seller |

## 🔐 인증 & 권한

### JWT 토큰 인증
```bash
# 로그인 후 받은 access_token을 헤더에 포함
Authorization: Bearer <access_token>
```

### 권한 레벨
| 권한 | 설명 |
|------|------|
| `user` | 일반 사용자 (기본) |
| `seller` | 판매자 (도서 등록 가능) |
| `admin` | 관리자 (전체 권한) |

## 📊 데이터베이스 스키마

### 주요 테이블 (13개)
- `user` - 사용자
- `sellerProfiles` - 판매자 프로필
- `book` - 도서
- `cart` - 장바구니
- `order` - 주문
- `orderItem` - 주문 상품
- `review` - 리뷰
- `favorite` - 찜하기
- `ranking` - 랭킹
- `saleInform` - 세일 정보
- `saleBookList` - 세일 도서 목록
- `settlement` - 정산
- `settlementOrder` - 정산 주문

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 테스트 파일 실행
pytest tests/test_auth.py

# 커버리지 측정
pytest --cov=app tests/
```

### 테스트 구성
| 파일 | 테스트 대상 | 테스트 케이스 |
|------|-------------|---------------|
| test_auth.py | 회원가입, 로그인, 토큰 | 12개 |
| test_users.py | 프로필, 비밀번호, 관리자 | 10개 |
| test_sellers.py | 판매자 등록, 조회, 수정 | 6개 |
| test_books.py | 도서 CRUD, 검색, 정렬 | 14개 |
| test_carts.py | 장바구니 CRUD | 10개 |
| test_orders.py | 주문 생성, 조회, 취소 | 10개 |
| test_reviews.py | 리뷰 작성, 조회, 삭제 | 10개 |
| test_favorites.py | 찜하기 등록, 취소, 조회 | 8개 |

## 📦 응답 형식

### 성공 응답
```json
{
  "status": "success",
  "data": { ... },
  "message": "Success message"
}
```

### 에러 응답
```json
{
  "status": "error",
  "data": null,
  "message": "Error message"
}
```

### HTTP 상태 코드
| 코드 | 상태 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 409 | Conflict | 리소스 중복 |
| 422 | Unprocessable Entity | 유효성 검증 실패 |
| 500 | Internal Server Error | 서버 에러 |

## ⚙️ 환경 설정

### .env 파일
```env
# Application
APP_NAME="BookStore API"
APP_VERSION="1.0.0"
DEBUG=True

# Database (MySQL)
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=bookStoreDb
MYSQL_USER=bookstore_user
MYSQL_PASSWORD=bookstore_pass
DATABASE_URL=mysql+pymysql://bookstore_user:bookstore_pass@db:3306/bookStoreDb

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 🐳 Docker 설정

### docker-compose.yml 구성
- **db**: MySQL 8.0 데이터베이스
  - 포트: 3306
  - 볼륨: db_data (영구 저장)
  - 헬스체크 포함
- **app**: FastAPI 애플리케이션
  - 포트: 8000
  - Hot Reload 지원
  - db 서비스 의존

### 명령어
```bash
# 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f app

# 종료
docker-compose down

# 볼륨 포함 삭제
docker-compose down -v
```

## 📁 프로젝트 구조 설명

### 레이어 아키텍처
```
API (Router) → Service → Repository → Model
     ↓            ↓           ↓          ↓
  HTTP 처리   비즈니스 로직   DB 쿼리   ORM 모델
```

### 레이어별 역할
| 레이어 | 파일 위치 | 역할 |
|--------|-----------|------|
| Router | `api/routers/` | HTTP 요청/응답 처리 |
| Service | `services/` | 비즈니스 로직, 예외 처리 |
| Repository | `repositories/` | DB CRUD 작업 |
| Model | `models/` | SQLAlchemy ORM 정의 |
| Schema | `schemas/` | Pydantic DTO 검증 |

## 🛠️ 개발 도구

### 코드 품질 도구

이 프로젝트는 다음 개발 도구들을 사용합니다:

| 도구 | 버전 | 용도 |
|------|------|------|
| **Black** | 24.10.0 | 코드 포맷팅 |
| **isort** | 5.13.2 | Import 정렬 |
| **Flake8** | 7.1.1 | 코드 린팅 |
| **mypy** | - | 타입 체킹 |
| **pre-commit** | - | Git Hook 자동화 |

### Pre-commit 설정

```bash
# pre-commit 설치
pip install pre-commit

# Git Hook 설치
pre-commit install

# 전체 파일 검사
pre-commit run --all-files
```

### 코드 스타일 규칙
- **Line Length**: 88자 (Black 기본값)
- **Python Version**: 3.12
- **Import 정렬**: Black 프로필 사용

## 🔧 기술 스택

### Backend
| 라이브러리 | 용도 |
|-----------|------|
| **FastAPI** | 웹 프레임워크 |
| **Uvicorn** | ASGI 서버 |
| **Gunicorn** | Production WSGI 서버 |
| **SQLAlchemy** | ORM |
| **Pydantic** | 데이터 검증 |
| **pydantic-settings** | 환경변수 관리 |

### 보안
| 라이브러리 | 용도 |
|-----------|------|
| **PyJWT** | JWT 토큰 생성/검증 |
| **pwdlib[argon2]** | Argon2id 비밀번호 해싱 (OWASP 권장) |
| **bcrypt** | 추가 해싱 지원 |
| **cryptography** | 암호화 라이브러리 |

### 데이터베이스
| 라이브러리 | 용도 |
|-----------|------|
| **PyMySQL** | MySQL 드라이버 |
| **MySQL 8.0** | DBMS |

### 테스트
| 라이브러리 | 용도 |
|-----------|------|
| **pytest** | 테스트 프레임워크 |
| **pytest-asyncio** | 비동기 테스트 |
| **httpx** | HTTP 테스트 클라이언트 |

## 📜 라이선스

이 프로젝트는 교육 목적으로 작성되었습니다.
