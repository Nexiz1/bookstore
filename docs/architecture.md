# 아키텍처 설계 문서

## 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│         (Postman, Web Frontend, Mobile App)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ Middleware │→ │  Routers   │→ │   Dependencies         │ │
│  │ - CORS     │  │ (API Layer)│  │ - Auth, DB Session     │ │
│  │ - Logging  │  └─────┬──────┘  └────────────────────────┘ │
│  │ - Rate     │        │                                     │
│  │   Limiter  │        ▼                                     │
│  └────────────┘  ┌────────────┐                             │
│                  │  Services  │  (Business Logic)            │
│                  └─────┬──────┘                             │
│                        │                                     │
│                        ▼                                     │
│                  ┌────────────┐                             │
│                  │Repositories│  (Data Access)               │
│                  └─────┬──────┘                             │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    MySQL     │  │    Redis     │  │  APScheduler │
│   Database   │  │    Cache     │  │  (Background)│
│              │  │              │  │    Tasks     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 계층 구조 (Layered Architecture)

### 1. **API Layer** (`app/api/`)
- **역할**: HTTP 요청 수신, 응답 반환, 요청 검증
- **주요 컴포넌트**:
  - `routers/`: 엔드포인트 정의 (auth, users, books, orders 등)
  - `dependencies.py`: 의존성 주입 (DB 세션, 인증, 권한 체크)

```
app/api/
├── routers/
│   ├── auth.py          # 인증 엔드포인트
│   ├── users.py         # 사용자 관리
│   ├── sellers.py       # 판매자 관리
│   ├── books.py         # 도서 CRUD
│   ├── carts.py         # 장바구니
│   ├── orders.py        # 주문
│   ├── reviews.py       # 리뷰
│   ├── favorites.py     # 찜하기
│   ├── rankings.py      # 랭킹
│   ├── sales.py         # 세일
│   └── admin.py         # 관리자
└── dependencies.py      # 공통 의존성
```

### 2. **Service Layer** (`app/services/`)
- **역할**: 비즈니스 로직 구현, 트랜잭션 관리
- **특징**:
  - Repository를 조합하여 복잡한 비즈니스 로직 처리
  - 트랜잭션 경계 설정 (예: `OrderService.create_order()`)

```
app/services/
├── auth_service.py         # 로그인, 회원가입, 토큰 발급
├── user_service.py         # 사용자 관리
├── seller_service.py       # 판매자 등록 및 관리
├── book_service.py         # 도서 CRUD
├── cart_service.py         # 장바구니 관리
├── order_service.py        # 주문 생성 (트랜잭션)
├── review_service.py       # 리뷰 작성 및 평점 업데이트
├── favorite_service.py     # 찜하기
├── ranking_service.py      # 랭킹 집계 및 캐싱
├── sale_service.py         # 세일 관리
└── settlement_service.py   # 정산 계산
```

### 3. **Repository Layer** (`app/repositories/`)
- **역할**: 데이터베이스 접근 추상화 (CRUD 연산)
- **특징**: SQLAlchemy ORM을 사용한 데이터 접근

```
app/repositories/
├── user_repository.py
├── seller_repository.py
├── book_repository.py
├── cart_repository.py
├── order_repository.py
├── review_repository.py
├── favorite_repository.py
├── ranking_repository.py
├── sale_repository.py
└── settlement_repository.py
```

### 4. **Model Layer** (`app/models/`)
- **역할**: 데이터베이스 테이블 정의 (SQLAlchemy 2.0 스타일)
- **특징**: Mapped 타입 사용, 관계 정의

```
app/models/
├── user.py           # User 테이블
├── seller.py         # Seller 테이블
├── book.py           # Book 테이블
├── cart.py           # Cart 테이블
├── order.py          # Order 테이블
├── order_item.py     # OrderItem 테이블
├── review.py         # Review 테이블
├── favorite.py       # Favorite 테이블
├── ranking.py        # Ranking 테이블 (캐시 전용)
├── sale.py           # Sale 테이블
├── settlement.py     # Settlement 테이블
└── settlement_order.py # SettlementOrder (M:N)
```

### 5. **Schema Layer** (`app/schemas/`)
- **역할**: 요청/응답 데이터 검증 (Pydantic)
- **특징**: DTO (Data Transfer Object) 역할

```
app/schemas/
├── user.py
├── seller.py
├── book.py
├── cart.py
├── order.py
├── review.py
├── favorite.py
├── ranking.py
├── sale.py
├── settlement.py
└── response.py      # 공통 응답 스키마
```

## 핵심 컴포넌트

### 1. 인증 시스템 (JWT)

```python
# app/core/security.py
- create_access_token()   # 15분 유효
- create_refresh_token()  # 7일 유효
- verify_password()
- get_password_hash()
```

**흐름:**
```
1. POST /auth/login → AuthService.login()
2. 비밀번호 검증 (bcrypt)
3. JWT 토큰 발급 (access + refresh)
4. 이후 요청: get_current_user() dependency로 인증
```

### 2. 캐싱 시스템 (Redis)

```python
# app/core/redis.py
- get_redis_client()           # Redis 연결
- RedisKeys.ranking_key()      # 캐시 키 생성

# app/services/ranking_service.py
- get_rankings_cached()        # 캐시 우선 조회
- calculate_and_cache_rankings() # 집계 후 캐싱
```

**캐싱 전략:**
- **TTL**: 10분 (RANKING_CACHE_TTL)
- **갱신**: APScheduler로 10분마다 자동 갱신
- **폴백**: 캐시 미스 시 DB 조회 → 캐싱

### 3. 스케줄러 (APScheduler)

```python
# app/main.py
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        refresh_rankings,
        trigger="interval",
        minutes=10,
        id="ranking_refresh"
    )
```

### 4. 트랜잭션 관리 (Unit of Work)

**예시: 주문 생성 (OrderService)**
```python
def create_order(self, user_id: int) -> OrderResponse:
    try:
        # 1. 장바구니 조회
        cart_items = self.cart_repo.get_by_user_id(user_id)

        # 2. 주문 생성 (commit=False)
        order = self.order_repo.create({...}, commit=False)

        # 3. 주문 아이템 생성 (commit=False)
        for cart in cart_items:
            self.order_item_repo.create({...}, commit=False)

        # 4. 장바구니 비우기 (commit=False)
        self.cart_repo.delete_all_by_user(user_id, commit=False)

        # 5. 도서 판매량 증가 (commit=False)
        self.book_repo.update_stats(book, purchase_count=...)

        # 6. 트랜잭션 커밋
        self.db.commit()

        return order
    except Exception as e:
        self.db.rollback()
        raise
```

## 의존성 주입 패턴

FastAPI의 `Depends()`를 사용한 의존성 주입:

```python
# app/api/dependencies.py
def get_db() -> Generator[Session, None, None]:
    """DB 세션 생성 및 자동 종료"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """JWT 토큰 검증 및 사용자 반환"""
    # ...

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """OrderService 인스턴스 생성"""
    return OrderService(db)
```

**사용 예시:**
```python
@router.post("/orders/")
def create_order(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.create_order(current_user.id)
```

## 미들웨어 스택

```python
# app/main.py
1. CORSMiddleware        # CORS 설정
2. SlowAPIMiddleware     # Rate Limiting
3. LoggingMiddleware     # 요청/응답 로깅
4. ExceptionHandlers     # 전역 예외 처리
```

## 데이터베이스 마이그레이션

**Alembic 사용:**
```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "message"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

## 테스트 아키텍처

```
tests/
├── conftest.py              # 공통 픽스처 및 헬퍼
├── test_auth.py
├── test_users.py
├── test_sellers.py
├── test_books.py
├── test_carts.py
├── test_orders.py
├── test_reviews.py
├── test_favorites.py
├── test_rankings.py
├── test_sales.py
└── test_admin.py
```

**테스트 전략:**
- **In-Memory SQLite**: 빠른 테스트 실행
- **Mock Redis**: 실제 Redis 불필요
- **Fixture 기반**: 재사용 가능한 테스트 데이터
- **Coverage**: 109개 테스트, 100% 통과

## 보안 고려사항

1. **비밀번호 암호화**: bcrypt 해싱
2. **JWT 보안**: 짧은 만료 시간 (15분)
3. **SQL Injection 방지**: SQLAlchemy ORM 사용
4. **Rate Limiting**: SlowAPI로 요청 제한
5. **CORS 설정**: 허용된 도메인만 접근
6. **환경 변수**: 민감 정보 .env 파일 관리

## 성능 최적화

1. **Redis 캐싱**: 랭킹 데이터 (10분 TTL)
2. **데이터베이스 인덱싱**: 외래 키, 검색 필드
3. **Lazy Loading**: SQLAlchemy 관계 설정
4. **Connection Pooling**: SQLAlchemy 엔진 설정
5. **비동기 Redis**: `redis.asyncio` 사용

## 확장 가능성

1. **수평 확장**: Stateless API 설계
2. **캐시 확장**: Redis Cluster 적용 가능
3. **DB 샤딩**: 판매자별/지역별 분리 가능
4. **마이크로서비스**: 도메인별 분리 가능
   - 인증 서비스
   - 주문 서비스
   - 정산 서비스
   - 랭킹 서비스

## 모니터링 및 로깅

```python
# app/middleware/logging_middleware.py
- 모든 요청/응답 로깅
- 실행 시간 측정
- 에러 추적
```

**로그 포맷:**
```
2025-12-14 12:34:56 | INFO | app.middleware:25 | → POST /orders/
2025-12-14 12:34:57 | INFO | app.middleware:41 | ← 201 (123.45ms)
```

## 배포 아키텍처

```
Docker Compose (개발/테스트)
├── app (FastAPI)
├── db (MySQL 8.0)
└── redis (Redis 7.0)

Production (권장)
├── Load Balancer (Nginx)
├── App Servers (Gunicorn + Uvicorn)
├── Database (MySQL RDS)
└── Cache (Redis ElastiCache)
```
