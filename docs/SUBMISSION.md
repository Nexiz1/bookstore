# GitHub 제출 가이드

## 제출물 체크리스트

### ✅ 필수 파일

- [x] **README.md**: 프로젝트 개요, 실행 방법, API 목록
- [x] **.gitignore**: Git 제외 파일 목록
- [x] **.env.example**: 환경변수 템플릿
- [x] **requirements.txt**: Python 의존성 목록
- [x] **docker-compose.yml**: Docker Compose 설정
- [x] **Dockerfile**: Docker 이미지 빌드 스크립트

### ✅ docs/ 디렉터리

- [x] **api-design.md**: API 설계 문서 (40개 엔드포인트)
- [x] **db-schema.md**: 데이터베이스 스키마 및 ERD
- [x] **architecture.md**: 시스템 아키텍처 및 계층 구조

### ✅ postman/ 디렉터리

- [x] **BookStore-API.postman_collection.json**: Postman 컬렉션 (API 테스트용)

### ✅ scripts/ 디렉터리

- [x] **seed.py**: 시드 데이터 생성 스크립트

### ✅ tests/ 디렉터리

- [x] **109개 테스트 파일** (100% 통과)
- [x] **conftest.py**: 공통 픽스처 및 헬퍼 함수

### ✅ app/ 디렉터리 (소스 코드)

- [x] **api/routers/**: 11개 라우터 (40개 엔드포인트)
- [x] **models/**: 12개 데이터베이스 모델
- [x] **services/**: 10개 서비스 계층
- [x] **repositories/**: 10개 리포지토리 계층
- [x] **schemas/**: Pydantic 스키마

---

## 프로젝트 구조 (GitHub 제출 형식)

```
bookstore-api/
├── README.md                          ✅ 프로젝트 개요 및 실행 가이드
├── .gitignore                         ✅ Git 제외 파일
├── .env.example                       ✅ 환경변수 템플릿
├── requirements.txt                   ✅ Python 의존성
├── docker-compose.yml                 ✅ Docker Compose 설정
├── Dockerfile                         ✅ Docker 이미지 빌드
│
├── docs/                              ✅ 문서 디렉터리
│   ├── api-design.md                  → API 설계 및 엔드포인트 목록
│   ├── db-schema.md                   → ERD 및 테이블 정의
│   └── architecture.md                → 시스템 아키텍처
│
├── postman/                           ✅ Postman 컬렉션
│   └── BookStore-API.postman_collection.json
│
├── scripts/                           ✅ 유틸리티 스크립트
│   └── seed.py                        → 시드 데이터 생성
│
├── tests/                             ✅ 자동화 테스트 (109개)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_sellers.py
│   ├── test_books.py
│   ├── test_carts.py
│   ├── test_orders.py
│   ├── test_reviews.py
│   ├── test_favorites.py
│   ├── test_rankings.py
│   └── test_admin.py
│
└── app/                               ✅ 애플리케이션 소스
    ├── main.py
    ├── api/
    ├── core/
    ├── models/
    ├── schemas/
    ├── services/
    ├── repositories/
    ├── exceptions/
    ├── middleware/
    └── utils/
```

---

## 실행 방법

### 1. Docker Compose로 실행 (권장)

```bash
# 1. 저장소 클론
git clone <repository-url>
cd bookstore-api

# 2. 환경변수 설정
cp .env.example .env
# .env 파일 수정 (MySQL 비밀번호 등)

# 3. 컨테이너 빌드 및 실행
docker-compose up --build

# 4. 시드 데이터 생성 (선택사항)
docker-compose exec app python scripts/seed.py

# 5. API 문서 확인
# http://localhost:8000/docs
```

### 2. 테스트 실행

```bash
# Docker 환경에서 테스트
docker-compose exec app pytest tests/ -v

# 로컬 환경에서 테스트
python -m pytest tests/ -v
```

**결과: 109개 테스트 모두 통과 (100%)**

---

## API 문서 확인 방법

### 1. Swagger UI (자동 생성)
- URL: `http://localhost:8000/docs`
- FastAPI가 자동 생성하는 인터랙티브 API 문서

### 2. ReDoc (자동 생성)
- URL: `http://localhost:8000/redoc`
- 읽기 전용 API 문서

### 3. Postman 컬렉션
- 파일: `postman/BookStore-API.postman_collection.json`
- Postman에서 Import하여 사용
- 인증 토큰 자동 저장 기능 포함

---

## 주요 기술 스택

### Backend
- **Framework**: FastAPI 0.115.x
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt

### Database & Cache
- **Database**: MySQL 8.0
- **Cache**: Redis 7.0
- **Migration**: Alembic

### Testing
- **Framework**: pytest
- **Coverage**: 109 tests (100% pass rate)

### Deployment
- **Containerization**: Docker + Docker Compose
- **WSGI Server**: Uvicorn

---

## 데이터베이스 정보

### ERD 확인
- 파일: `docs/db-schema.md`
- 12개 테이블 정의
- 관계도 및 제약 조건 포함

### 테이블 목록
1. **user** - 사용자
2. **seller** - 판매자
3. **book** - 도서
4. **cart** - 장바구니
5. **order** - 주문
6. **orderItem** - 주문 아이템
7. **review** - 리뷰
8. **favorite** - 찜하기
9. **ranking** - 랭킹 (캐시용)
10. **sale** - 타임 세일
11. **settlement** - 정산
12. **settlementOrder** - 정산-주문 매핑

---

## API 엔드포인트 요약

### 총 40개 엔드포인트

| 카테고리 | 개수 | 주요 기능 |
|---------|------|----------|
| 인증 (Auth) | 4 | 회원가입, 로그인, 토큰 재발급 |
| 사용자 (Users) | 6 | 프로필 관리, 비밀번호 변경, 계정 관리 |
| 판매자 (Sellers) | 3 | 판매자 등록, 정보 수정, 정산 조회 |
| 도서 (Books) | 5 | 도서 CRUD, 검색/필터/정렬 |
| 장바구니 (Carts) | 4 | 장바구니 CRUD |
| 주문 (Orders) | 4 | 주문 생성, 조회, 취소 |
| 리뷰 (Reviews) | 5 | 리뷰 CRUD, 평점 관리 |
| 찜하기 (Favorites) | 3 | 찜 등록/취소/조회 |
| 랭킹 (Rankings) | 1 | Redis 캐싱 기반 랭킹 |
| 세일 (Sales) | 2 | 타임 세일 관리 |
| 관리자 (Admin) | 2 | 전체 주문 조회, 정산 생성 |
| 정산 (Settlements) | 1 | 판매자 정산 내역 |

**상세 내용**: `docs/api-design.md` 참조

---

## 핵심 기능

### 1. JWT 인증
- Access Token (15분) + Refresh Token (7일)
- 역할 기반 접근 제어 (user, seller, admin)

### 2. Redis 캐싱
- 랭킹 데이터 10분 TTL 캐싱
- APScheduler로 10분마다 자동 갱신

### 3. 트랜잭션 관리
- Unit of Work 패턴
- 주문 생성 시 원자성 보장

### 4. 테스트 커버리지
- 109개 테스트 (100% 통과)
- In-Memory SQLite 사용
- Mock Redis 사용

### 5. 정산 시스템
- 판매자별 매출 집계
- 10% 수수료 자동 계산
- 중복 정산 방지 (is_settled 플래그)

---

## 성능 최적화

1. **Redis 캐싱**: 랭킹 데이터 캐시로 DB 부하 감소
2. **데이터베이스 인덱싱**: 주요 조회 컬럼에 인덱스 적용
3. **페이지네이션**: 목록 조회 API 페이지네이션
4. **Connection Pooling**: SQLAlchemy 엔진 설정
5. **비동기 Redis**: redis.asyncio 사용

---

## 보안 고려사항

1. **비밀번호 암호화**: bcrypt 해싱
2. **JWT 토큰**: 짧은 만료 시간 설정
3. **Rate Limiting**: SlowAPI 요청 제한
4. **CORS 설정**: 허용 Origin 명시
5. **계정 비활성화**: 관리자 권한
6. **SQL Injection 방지**: ORM 사용

---

## 문의 및 지원

- **학번**: 202111666
- **작성자**: 최진서
- **GitHub**: [Repository URL]
- **API 문서**: http://localhost:8000/docs

---

## 라이선스

이 프로젝트는 교육 목적으로 작성되었습니다.
