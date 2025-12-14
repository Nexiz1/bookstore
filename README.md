# BookStore API

온라인 서점 백엔드 API - FastAPI + MySQL + Redis + Docker Compose

---

## 프로젝트 개요

### 문제 정의
온라인 서점 플랫폼의 백엔드 API 서버로, 도서 판매/구매, 리뷰, 랭킹, 정산 등의 핵심 기능을 제공합니다.

### 기본 정보
| 항목 | 내용 |
|------|------|
| **학번** | 202111666 |
| **작성자** | 최진서 |
| **DBMS** | MySQL 8.0 |
| **Cache** | Redis (랭킹 캐싱) |
| **DB Name** | bookStoreDb |
| **API 개수** | 40개 엔드포인트 |
| **Python** | 3.12 |
| **Framework** | FastAPI |

### 주요 기능 목록
- **인증/회원**: 회원가입, JWT 로그인, 토큰 재발급, 프로필 관리
- **판매자**: 판매자 등록 신청, 판매자 정보 관리
- **도서**: 도서 CRUD, 검색/필터/정렬
- **장바구니**: 장바구니 CRUD
- **주문**: 주문 생성, 조회, 취소
- **리뷰**: 리뷰 작성/수정/삭제, 평점 관리
- **찜하기**: 찜 등록/취소
- **랭킹**: Redis 캐싱 기반 실시간 랭킹 (10분 주기 갱신)
- **세일**: 타임 세일 생성/관리
- **정산**: 판매자 정산 데이터 생성/조회
- **관리자**: 사용자 관리, 권한 변경, 계정 비활성화

---

## 실행 방법

### Docker Compose (권장)

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일 수정 (아래 환경변수 설명 참조)

# 2. 컨테이너 빌드 및 실행
docker-compose up --build

# 3. 시드 데이터 생성 (선택)
docker-compose exec app python scripts/seed.py

# 4. API 문서 확인
# http://localhost:8000/docs
```

### 로컬 실행

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# DATABASE_URL, REDIS_URL 수정

# 4. 데이터베이스 마이그레이션 (Alembic 사용 시)
alembic upgrade head

# 5. 시드 데이터 생성 (선택)
python scripts/seed.py

# 6. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### VS Code DevContainer

1. VS Code에서 프로젝트 열기
2. `F1` → `Dev Containers: Reopen in Container` 선택
3. 자동으로 MySQL + Redis + FastAPI 환경 구성

---

## 환경변수 설명

`.env.example` 파일 참조:

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `APP_NAME` | 애플리케이션 이름 | `"BookStore API"` |
| `APP_VERSION` | 애플리케이션 버전 | `"1.0.0"` |
| `DEBUG` | 디버그 모드 | `True` |
| `DATABASE_URL` | MySQL 연결 문자열 | `mysql+pymysql://user:pass@db:3306/bookStoreDb` |
| `REDIS_URL` | Redis 연결 문자열 | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT 서명 비밀키 (프로덕션에서 변경 필수) | `your-secret-key...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 시간 (분) | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 시간 (일) | `7` |
| `LOG_LEVEL` | 로깅 레벨 | `DEBUG` |
| `CORS_ORIGINS` | 허용할 CORS Origin 목록 | `["http://localhost:3000"]` |

---

## 배포 주소

| 항목 | URL |
|------|-----|
| **Base URL** | `http://localhost:8000` |
| **Swagger UI** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |
| **Health Check** | `http://localhost:8000/health` |

---

## 인증 플로우 설명

### JWT 토큰 기반 인증

```
1. 회원가입 (POST /auth/signup)
   └─> 사용자 계정 생성

2. 로그인 (POST /auth/login)
   └─> access_token + refresh_token 발급

3. API 요청 시 헤더에 토큰 포함
   Authorization: Bearer <access_token>

4. 토큰 만료 시 재발급 (POST /auth/refresh)
   └─> 새로운 access_token 발급

5. 로그아웃 (POST /auth/logout)
   └─> 클라이언트에서 토큰 삭제
```

### 토큰 구조
- **Access Token**: 30분 유효 (API 인증용)
- **Refresh Token**: 7일 유효 (Access Token 재발급용)
- **알고리즘**: HS256
- **비밀번호 해싱**: Argon2id (OWASP 권장)

---

## 역할/권한표

| 권한 | 설명 | 접근 가능 API |
|------|------|--------------|
| `user` | 일반 사용자 (기본) | 도서 조회, 장바구니, 주문, 리뷰, 찜하기 |
| `seller` | 판매자 | user 권한 + 도서 등록/관리, 세일 생성, 정산 조회 |
| `admin` | 관리자 | 전체 권한 + 사용자 관리, 권한 변경, 계정 비활성화, 정산 생성 |

### 역할별 API 접근 권한

| API | Anyone | User | Seller | Admin |
|-----|--------|------|--------|-------|
| 회원가입/로그인 | O | O | O | O |
| 도서 목록/상세 조회 | O | O | O | O |
| 랭킹 조회 | O | O | O | O |
| 프로필 조회/수정 | - | O | O | O |
| 장바구니 CRUD | - | O | - | O |
| 주문 생성/조회/취소 | - | O | - | O |
| 리뷰 작성/수정/삭제 | - | O | O | O |
| 찜하기 등록/취소 | - | O | O | O |
| 도서 등록/수정/삭제 | - | - | O | O |
| 세일 생성 | - | - | O | O |
| 정산 조회 | - | - | O | O |
| 전체 사용자 조회 | - | - | - | O |
| 사용자 권한 변경 | - | - | - | O |
| 사용자 계정 비활성화 | - | - | - | O |
| 정산 데이터 생성 | - | - | - | O |
| 전체 주문 현황 조회 | - | - | - | O |

---

## 예제 계정

시드 데이터 실행 후 사용 가능:

| 역할 | 이메일 | 비밀번호 | 비고 |
|------|--------|----------|------|
| **Admin** | `admin@bookstore.com` | `admin123!` | 전체 관리 권한 |
| **User** | `user1@xxx.com` ~ `user49@xxx.com` | `password123!` | 일반 사용자 |

> **주의**: Admin 계정은 모든 데이터에 접근 가능합니다. 프로덕션에서는 비밀번호를 반드시 변경하세요.

---

## DB 연결 정보 (테스트용)

Docker Compose 환경:

| 항목 | 값 |
|------|-----|
| **Host** | `localhost` (외부) / `db` (Docker 내부) |
| **Port** | `3306` |
| **Database** | `bookStoreDb` |
| **Username** | `bookstore_user` |
| **Password** | `.env` 파일 참조 |
| **권한** | bookStoreDb 데이터베이스 전체 권한 |

Redis:

| 항목 | 값 |
|------|-----|
| **Host** | `localhost` (외부) / `redis` (Docker 내부) |
| **Port** | `6379` |
| **Database** | `0` |

---

## 프로젝트 구조

```
repo-root/
├── README.md                          # 프로젝트 개요 및 실행 방법
├── .gitignore                         # Git 제외 파일
├── .env.example                       # 환경변수 템플릿
├── requirements.txt                   # Python 의존성
├── pyproject.toml                     # Python 프로젝트 설정
├── pytest.ini                         # pytest 설정
├── docker-compose.yml                 # Docker Compose 설정
├── Dockerfile                         # Docker 이미지 빌드
├── alembic.ini                        # Alembic 설정
│
├── docs/                              # 📁 문서
│   ├── api-design.md                  # API 설계 문서
│   ├── db-schema.md                   # 데이터베이스 스키마 (ERD)
│   └── architecture.md                # 아키텍처 설계 문서
│
├── postman/                           # 📁 Postman 컬렉션
│   └── BookStore-API.postman_collection.json
│
├── scripts/                           # 📁 유틸리티 스크립트
│   ├── __init__.py
│   └── seed.py                        # 시드 데이터 생성
│
├── alembic/                           # 📁 데이터베이스 마이그레이션
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                      # 마이그레이션 파일들
│
├── tests/                             # 📁 테스트 (109개, 100% 통과)
│   ├── conftest.py                    # 공통 픽스처 및 헬퍼
│   ├── test_auth.py                   # 인증 테스트
│   ├── test_users.py                  # 사용자 테스트
│   ├── test_sellers.py                # 판매자 테스트
│   ├── test_books.py                  # 도서 테스트
│   ├── test_carts.py                  # 장바구니 테스트
│   ├── test_orders.py                 # 주문 테스트
│   ├── test_reviews.py                # 리뷰 테스트
│   ├── test_favorites.py              # 찜하기 테스트
│   ├── test_rankings.py               # 랭킹 테스트
│   └── test_admin.py                  # 관리자 테스트
│
└── app/                               # 📁 애플리케이션 소스
    ├── __init__.py
    ├── main.py                        # FastAPI 앱 진입점
    │
    ├── api/                           # 📁 API 라우터
    │   ├── dependencies.py            # 의존성 주입 (인증, DB 세션)
    │   └── routers/
    │       ├── auth.py                # 인증 API
    │       ├── users.py               # 사용자 API
    │       ├── sellers.py             # 판매자 API
    │       ├── books.py               # 도서 API
    │       ├── carts.py               # 장바구니 API
    │       ├── orders.py              # 주문 API
    │       ├── reviews.py             # 리뷰 API
    │       ├── favorites.py           # 찜하기 API
    │       ├── rankings.py            # 랭킹 API
    │       ├── sales.py               # 세일 API
    │       └── admin.py               # 관리자 API
    │
    ├── core/                          # 📁 핵심 설정
    │   ├── config.py                  # 환경변수 로드
    │   ├── database.py                # SQLAlchemy 설정
    │   ├── redis.py                   # Redis 연결
    │   └── security.py                # JWT, 비밀번호 해싱
    │
    ├── models/                        # 📁 데이터베이스 모델 (ORM)
    │   ├── user.py
    │   ├── seller.py
    │   ├── book.py
    │   ├── cart.py
    │   ├── order.py
    │   ├── order_item.py
    │   ├── review.py
    │   ├── favorite.py
    │   ├── ranking.py
    │   ├── sale.py
    │   ├── settlement.py
    │   └── settlement_order.py
    │
    ├── schemas/                       # 📁 Pydantic 스키마 (DTO)
    │   ├── user.py
    │   ├── seller.py
    │   ├── book.py
    │   ├── cart.py
    │   ├── order.py
    │   ├── review.py
    │   ├── favorite.py
    │   ├── ranking.py
    │   ├── sale.py
    │   ├── settlement.py
    │   └── response.py                # 공통 응답 스키마
    │
    ├── services/                      # 📁 비즈니스 로직
    │   ├── auth_service.py
    │   ├── user_service.py
    │   ├── seller_service.py
    │   ├── book_service.py
    │   ├── cart_service.py
    │   ├── order_service.py
    │   ├── review_service.py
    │   ├── favorite_service.py
    │   ├── ranking_service.py
    │   ├── sale_service.py
    │   └── settlement_service.py
    │
    ├── repositories/                  # 📁 데이터 접근 계층
    │   ├── user_repository.py
    │   ├── seller_repository.py
    │   ├── book_repository.py
    │   ├── cart_repository.py
    │   ├── order_repository.py
    │   ├── review_repository.py
    │   ├── favorite_repository.py
    │   ├── ranking_repository.py
    │   ├── sale_repository.py
    │   └── settlement_repository.py
    │
    ├── exceptions/                    # 📁 커스텀 예외
    │   ├── auth_exceptions.py
    │   ├── user_exceptions.py
    │   ├── seller_exceptions.py
    │   ├── book_exceptions.py
    │   ├── cart_exceptions.py
    │   ├── order_exceptions.py
    │   └── review_exceptions.py
    │
    ├── middleware/                    # 📁 미들웨어
    │   ├── logging_middleware.py      # 요청/응답 로깅
    │   └── exception_handler.py       # 전역 예외 처리
    │
    └── utils/                         # 📁 유틸리티
        └── scheduler.py               # APScheduler (랭킹 갱신)
```

### 주요 디렉터리 설명

- **`docs/`**: API 설계, DB 스키마, 아키텍처 문서
- **`postman/`**: Postman 컬렉션 (API 테스트용)
- **`scripts/`**: 시드 데이터 생성 등 유틸리티 스크립트
- **`tests/`**: 109개 테스트 (100% 통과)
- **`app/api/`**: FastAPI 라우터 (엔드포인트 정의)
- **`app/core/`**: 설정, DB 연결, Redis, JWT 등 핵심 기능
- **`app/models/`**: SQLAlchemy ORM 모델
- **`app/schemas/`**: Pydantic 스키마 (요청/응답 검증)
- **`app/services/`**: 비즈니스 로직 계층
- **`app/repositories/`**: 데이터 접근 추상화 계층

---

## 엔드포인트 요약표 (Total: 40)

### 1. 인증 (Auth) - 4개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/auth/signup` | 회원가입 | Anyone |
| POST | `/auth/login` | 로그인 (JWT 발급) | Anyone |
| POST | `/auth/refresh` | 토큰 재발급 | Anyone |
| POST | `/auth/logout` | 로그아웃 | User/Seller/Admin |

### 2. 회원 (Users) - 6개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/users/me` | 내 프로필 조회 | User/Seller/Admin |
| PATCH | `/users/me` | 내 프로필 수정 | User/Seller/Admin |
| POST | `/users/me/password` | 비밀번호 변경 | User/Seller/Admin |
| GET | `/users` | 전체 회원 목록 | Admin |
| PATCH | `/users/{user_id}/role` | 회원 권한 변경 | Admin |
| PATCH | `/users/{user_id}/deactivate` | 계정 비활성화 | Admin |

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

### 6. 주문 (Orders) - 4개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/orders` | 주문 생성 | User |
| GET | `/orders` | 내 주문 내역 조회 | User |
| GET | `/orders/{order_id}` | 주문 상세 조회 | User |
| POST | `/orders/{order_id}/cancel` | 주문 취소 | User |

### 7. 리뷰 (Reviews) - 5개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/books/{book_id}/reviews` | 리뷰 작성 | User (구매자) |
| GET | `/books/{book_id}/reviews` | 리뷰 목록 조회 | Anyone |
| PATCH | `/books/{book_id}/reviews/{review_id}` | 리뷰 수정 | User (작성자) |
| PATCH | `/reviews/{review_id}` | 리뷰 수정 (레거시) | User (작성자) |
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
| GET | `/rankings` | 랭킹 조회 (type, ageGroup, gender, limit) | Anyone |

### 10. 세일 (Sales) - 2개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/sales` | 타임 세일 생성 | Seller |
| POST | `/sales/{sale_id}/books` | 세일 도서 추가 | Seller |

### 11. 정산 (Settlements) - 1개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/settlements` | 정산 내역 조회 | Seller |

### 12. 관리자 (Admin) - 2개
| Method | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/admin/orders` | 전체 주문 현황 | Admin |
| POST | `/admin/settlements/calculate` | 정산 데이터 생성 | Admin |

---

## 성능/보안 고려사항

### 성능 최적화
- **Redis 캐싱**: 랭킹 데이터를 Redis에 캐싱하여 DB 부하 감소
- **스케줄러**: APScheduler로 10분마다 랭킹 데이터 자동 갱신
- **페이지네이션**: 목록 조회 API에 페이지네이션 적용
- **인덱스**: 주요 조회 컬럼에 DB 인덱스 적용 (email, isbn, status 등)

### 보안
- **비밀번호 해싱**: Argon2id (OWASP 권장 알고리즘)
- **JWT 토큰**: Access/Refresh 토큰 분리, 만료 시간 설정
- **Rate Limiting**: slowapi를 통한 IP 기반 요청 제한
- **CORS**: 허용 Origin 명시적 설정
- **계정 비활성화**: 관리자가 사용자 계정 비활성화 가능
- **권한 검증**: 모든 엔드포인트에 역할 기반 접근 제어

### 데이터 무결성
- **트랜잭션**: Unit of Work 패턴으로 원자성 보장
- **외래 키**: SQLAlchemy 관계 설정으로 참조 무결성 유지

---

## 한계와 개선 계획

### 현재 한계
1. **검색 기능**: 단순 LIKE 검색 (Full-text search 미지원)
2. **파일 업로드**: 도서 이미지 업로드 미구현
3. **결제 시스템**: 실제 PG 연동 없음
4. **알림 시스템**: 푸시 알림 미구현
5. **다국어 지원**: 한국어만 지원

### 개선 계획
1. **Elasticsearch 도입**: 고급 검색 기능
2. **S3 연동**: 이미지 파일 저장
3. **WebSocket**: 실시간 알림
4. **CI/CD**: GitHub Actions 파이프라인 구축
5. **모니터링**: Prometheus + Grafana 연동
6. **테스트 커버리지**: 90% 이상 목표

---

## 아키텍처

### 프로젝트 구조
```
app/
├── api/                    # Presentation Layer
│   ├── routers/           # 12개 API 라우터
│   │   ├── auth.py        # 인증 (4 endpoints)
│   │   ├── users.py       # 회원 (6 endpoints)
│   │   ├── sellers.py     # 판매자 (3 endpoints)
│   │   ├── books.py       # 도서 (5 endpoints)
│   │   ├── carts.py       # 장바구니 (4 endpoints)
│   │   ├── orders.py      # 주문 (4 endpoints)
│   │   ├── reviews.py     # 리뷰 (5 endpoints)
│   │   ├── favorites.py   # 찜하기 (3 endpoints)
│   │   ├── rankings.py    # 랭킹 (1 endpoint)
│   │   ├── sales.py       # 세일 (2 endpoints)
│   │   ├── settlements.py # 정산 (1 endpoint)
│   │   └── admin.py       # 관리자 (2 endpoints)
│   └── dependencies.py    # 의존성 주입 & JWT 인증
├── services/              # Business Logic Layer
├── repositories/          # Data Access Layer
├── models/                # SQLAlchemy ORM Models (13개 테이블)
├── schemas/               # Pydantic DTOs
├── core/
│   ├── config.py          # 환경 설정
│   ├── database.py        # DB 연결
│   ├── redis.py           # Redis 연결
│   ├── limiter.py         # Rate Limiter
│   └── security.py        # JWT & 비밀번호 해싱
├── exceptions/            # 커스텀 예외 & 핸들러
├── middleware/            # 로깅 미들웨어
└── main.py                # Application Entry Point

tests/                     # 테스트 코드
├── conftest.py            # pytest fixtures (Redis Mocking 포함)
├── test_auth.py           # 인증 테스트
├── test_users.py          # 사용자 테스트 (계정 비활성화 포함)
├── test_sellers.py        # 판매자 테스트
├── test_books.py          # 도서 테스트
├── test_carts.py          # 장바구니 테스트
├── test_orders.py         # 주문 테스트
├── test_reviews.py        # 리뷰 테스트 (수정 기능 포함)
├── test_favorites.py      # 찜하기 테스트
├── test_admin.py          # 관리자 테스트 (정산 기능)
└── test_rankings.py       # 랭킹 테스트

scripts/
└── seed.py                # 시드 데이터 생성 스크립트
```

### 레이어 아키텍처
```
API (Router) → Service → Repository → Model
     ↓            ↓           ↓          ↓
  HTTP 처리   비즈니스 로직   DB 쿼리   ORM 모델
```

---

## 테스트

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
| 파일 | 테스트 대상 | 주요 테스트 케이스 |
|------|-------------|-------------------|
| test_auth.py | 회원가입, 로그인, 토큰 | 12개 |
| test_users.py | 프로필, 비밀번호, 권한, 계정 비활성화 | 16개 |
| test_sellers.py | 판매자 등록, 조회, 수정 | 6개 |
| test_books.py | 도서 CRUD, 검색, 정렬 | 14개 |
| test_carts.py | 장바구니 CRUD | 10개 |
| test_orders.py | 주문 생성, 조회, 취소 | 10개 |
| test_reviews.py | 리뷰 작성, 수정, 삭제 | 18개 |
| test_favorites.py | 찜하기 등록, 취소, 조회 | 8개 |
| test_admin.py | 관리자 주문 조회, 정산 생성 | 8개 |
| test_rankings.py | 랭킹 조회, 캐싱 | 7개 |

---

## 응답 형식

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
  "message": "Error message",
  "error_code": "ERROR_CODE"
}
```

### HTTP 상태 코드
| 코드 | 상태 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 필요 또는 비활성화된 계정 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 409 | Conflict | 리소스 중복 |
| 422 | Unprocessable Entity | 유효성 검증 실패 |
| 429 | Too Many Requests | Rate Limit 초과 |
| 500 | Internal Server Error | 서버 에러 |

---

## 기술 스택

### Backend
| 라이브러리 | 용도 |
|-----------|------|
| **FastAPI** | 웹 프레임워크 |
| **Uvicorn** | ASGI 서버 |
| **SQLAlchemy** | ORM |
| **Pydantic** | 데이터 검증 |
| **APScheduler** | 스케줄링 (랭킹 캐시 갱신) |

### 데이터베이스 & 캐시
| 라이브러리 | 용도 |
|-----------|------|
| **MySQL 8.0** | RDBMS |
| **Redis** | 캐시 (랭킹 데이터) |
| **PyMySQL** | MySQL 드라이버 |
| **redis-py** | Redis 클라이언트 |
| **Alembic** | DB 마이그레이션 |

### 보안
| 라이브러리 | 용도 |
|-----------|------|
| **PyJWT** | JWT 토큰 |
| **pwdlib[argon2]** | Argon2id 비밀번호 해싱 |
| **slowapi** | Rate Limiting |

### 테스트
| 라이브러리 | 용도 |
|-----------|------|
| **pytest** | 테스트 프레임워크 |
| **pytest-asyncio** | 비동기 테스트 |
| **httpx** | HTTP 테스트 클라이언트 |

---

## Docker 설정

### docker-compose.yml 구성
- **db**: MySQL 8.0 데이터베이스 (포트: 3306)
- **redis**: Redis 캐시 서버 (포트: 6379)
- **app**: FastAPI 애플리케이션 (포트: 8000)

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

---

## 라이선스

이 프로젝트는 교육 목적으로 작성되었습니다.
