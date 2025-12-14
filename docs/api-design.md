# API 설계 문서

## 개요
BookStore API는 RESTful 설계 원칙을 따르며, FastAPI 프레임워크를 사용하여 구현되었습니다.

## 엔드포인트 목록 (Total: 36)

### 1. 인증 (Authentication) - 4개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/auth/signup` | 회원가입 | Public |
| POST | `/auth/login` | 로그인 (JWT 발급) | Public |
| POST | `/auth/refresh` | Access Token 재발급 | Public |
| POST | `/auth/logout` | 로그아웃 | User |

**Request/Response 예시:**

```json
// POST /auth/signup - Request
{
  "email": "user@example.com",
  "password": "password123",
  "name": "홍길동",
  "gender": "male",
  "address": "서울시 강남구"
}

// POST /auth/signup - Response (201)
{
  "status": "success",
  "data": {
    "id": 51,
    "email": "user@example.com",
    "name": "홍길동",
    "role": "user",
    "is_active": true,
    "created_at": "2025-12-14T20:08:44"
  },
  "message": "User registered successfully"
}

// POST /auth/login - Request
{
  "email": "user@example.com",
  "password": "password123"
}

// POST /auth/login - Response (200)
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  },
  "message": "Login successful"
}
```

### 2. 사용자 (Users) - 6개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/users/me` | 내 프로필 조회 | User |
| PATCH | `/users/me` | 내 프로필 수정 | User |
| POST | `/users/me/password` | 비밀번호 변경 | User |
| GET | `/users/` | 전체 사용자 조회 | Admin |
| PATCH | `/users/{user_id}/role` | 사용자 권한 변경 | Admin |
| PATCH | `/users/{user_id}/deactivate` | 사용자 비활성화 | Admin |

**Request/Response 예시:**

```json
// PATCH /users/me - Request
{
  "name": "홍길동",
  "address": "서울시 서초구"
}

// POST /users/me/password - Request
{
  "current_password": "password123",
  "new_password": "newpassword456"
}

// PATCH /users/{user_id}/role - Request
{
  "role": "seller"
}

// PATCH /users/{user_id}/deactivate - Response (200)
{
  "status": "success",
  "data": {
    "id": 2,
    "email": "user1@daum.net",
    "name": "이상현",
    "role": "seller",
    "is_active": false,
    "created_at": "2025-12-14T19:58:37"
  },
  "message": "User account deactivated successfully"
}
```

### 3. 판매자 (Sellers) - 3개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/sellers/` | 판매자 등록 신청 | User |
| GET | `/sellers/me` | 내 판매자 정보 조회 | Seller |
| GET | `/settlements/` | 내 정산 내역 조회 | Seller |

**Request/Response 예시:**

```json
// POST /sellers/ - Request
{
  "business_name": "북스토어",
  "business_number": "123-45-67890",
  "email": "seller@example.com",
  "address": "서울시 강남구",
  "phone_number": "02-1234-5678",
  "payout_account": "110-123-456789",
  "payout_holder": "홍길동"
}

// POST /sellers/ - Response (201)
{
  "status": "success",
  "data": {
    "id": 11,
    "user_id": 51,
    "business_name": "북스토어",
    "business_number": "123-45-67890",
    "email": "seller@example.com",
    "created_at": "2025-12-14T20:36:29"
  },
  "message": "Seller registration successful"
}

// GET /settlements/ - Query Parameters
?startDate=2025-01-01&endDate=2025-12-31
```

### 4. 도서 (Books) - 5개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/books/` | 도서 등록 | Seller |
| GET | `/books/` | 도서 목록 조회 (검색/필터) | Public |
| GET | `/books/{book_id}` | 도서 상세 조회 | Public |
| PUT | `/books/{book_id}` | 도서 정보 수정 | Seller (본인) |
| DELETE | `/books/{book_id}` | 도서 삭제 | Seller (본인) |

**Request/Response 예시:**

```json
// POST /books/ - Request
{
  "title": "파이썬 완벽 가이드",
  "author": "홍길동",
  "publisher": "출판사",
  "summary": "파이썬 입문서",
  "isbn": "978-89-1234-5",
  "price": 25000,
  "status": "ONSALE"
}

// GET /books/ - Query Parameters
?page=1&size=10&keyword=파이썬&sort=price_asc

// GET /books/ - Response (200)
{
  "status": "success",
  "data": {
    "books": [
      {
        "id": 101,
        "seller_id": 11,
        "title": "파이썬 완벽 가이드",
        "author": "홍길동",
        "publisher": "출판사",
        "isbn": "978-89-1234-5",
        "price": "25000.00",
        "status": "ONSALE",
        "average_rating": "0.00",
        "review_count": 0,
        "purchase_count": 0
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10
  },
  "message": null
}

// PUT /books/{book_id} - Request
{
  "price": 20000,
  "status": "ONSALE"
}
```

### 5. 장바구니 (Carts) - 4개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/carts/` | 내 장바구니 조회 | User |
| POST | `/carts/` | 장바구니에 추가 | User |
| PATCH | `/carts/{cart_id}` | 장바구니 수량 변경 | User |
| DELETE | `/carts/{cart_id}` | 장바구니에서 제거 | User |

**Request/Response 예시:**

```json
// POST /carts/ - Request
{
  "book_id": 101,
  "quantity": 2
}

// POST /carts/ - Response (201)
{
  "status": "success",
  "data": {
    "id": 33,
    "book_id": 101,
    "book_title": "파이썬 완벽 가이드",
    "book_price": "25000.00",
    "quantity": 2,
    "subtotal": "50000.00",
    "created_at": "2025-12-14T20:43:28"
  },
  "message": "Item added to cart"
}

// PATCH /carts/{cart_id} - Request
{
  "quantity": 3
}
```

### 6. 주문 (Orders) - 4개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/orders/` | 주문 생성 (장바구니 → 주문) | User |
| GET | `/orders/` | 내 주문 목록 조회 | User |
| GET | `/orders/{order_id}` | 주문 상세 조회 | User (본인) |
| POST | `/orders/{order_id}/cancel` | 주문 취소 | User (본인) |

**Request/Response 예시:**

```json
// POST /orders/ - Request
{}

// POST /orders/ - Response (201)
{
  "status": "success",
  "data": {
    "id": 51,
    "user_id": 51,
    "order_date": "2025-12-14T20:10:05",
    "total_amount": "26000.00",
    "status": "CREATED",
    "items": [
      {
        "id": 154,
        "book_id": 1,
        "book_title": "올바른 사이즈의 물류 생산 능력",
        "price": "13000.00",
        "quantity": 2,
        "total_amount": "26000.00"
      }
    ],
    "created_at": "2025-12-14T20:10:05"
  },
  "message": "Order created successfully"
}

// POST /orders/{order_id}/cancel - Response (200)
{
  "status": "success",
  "data": {
    "id": 51,
    "status": "REFUND",
    ...
  },
  "message": "Order cancelled successfully"
}
```

### 7. 리뷰 (Reviews) - 4개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/books/{book_id}/reviews` | 리뷰 작성 (구매자만) | User |
| GET | `/books/{book_id}/reviews` | 도서 리뷰 목록 조회 | Public |
| PATCH | `/reviews/{review_id}` | 리뷰 수정 | User (본인) |
| DELETE | `/reviews/{review_id}` | 리뷰 삭제 | User (본인) or Admin |

**Request/Response 예시:**

```json
// POST /books/{book_id}/reviews - Request
{
  "order_item_id": 155,
  "rating": 5,
  "comment": "정말 좋은 책입니다!"
}

// POST /books/{book_id}/reviews - Response (201)
{
  "status": "success",
  "data": {
    "id": 30,
    "user_id": 51,
    "user_name": "홍길동",
    "book_id": 101,
    "rating": 5,
    "comment": "정말 좋은 책입니다!",
    "created_at": "2025-12-14T21:53:13"
  },
  "message": "Review created successfully"
}

// PATCH /reviews/{review_id} - Request
{
  "rating": 4,
  "comment": "수정된 리뷰입니다."
}

// GET /books/{book_id}/reviews - Response (200)
{
  "status": "success",
  "data": {
    "reviews": [...],
    "total": 1,
    "average_rating": 5
  },
  "message": null
}
```

### 8. 찜하기 (Favorites) - 3개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/books/{book_id}/favorites/` | 찜 추가 | User |
| GET | `/favorites/` | 내 찜 목록 조회 | User |
| DELETE | `/books/{book_id}/favorites` | 찜 취소 | User |

**Request/Response 예시:**

```json
// POST /books/{book_id}/favorites/ - Response (201)
{
  "status": "success",
  "data": {
    "id": 52,
    "book_id": 2,
    "book_title": "유저 친화적 5세대 허브",
    "book_author": "강은서",
    "book_price": "34000.00",
    "created_at": "2025-12-14T20:21:47"
  },
  "message": "Added to favorites"
}

// GET /favorites/ - Response (200)
{
  "status": "success",
  "data": {
    "favorites": [...],
    "total": 2
  },
  "message": null
}
```

### 9. 랭킹 (Rankings) - 1개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/rankings/` | 도서 랭킹 조회 (Redis 캐시) | Public |

**Query Parameters:**
- `type`: `purchaseCount` (판매량) or `averageRating` (평점) - 기본값: `purchaseCount`
- `limit`: 결과 개수 (기본: 10)

**Request/Response 예시:**

```json
// GET /rankings/?type=purchaseCount&limit=10 - Response (200)
{
  "status": "success",
  "data": {
    "ranking_type": "purchaseCount",
    "age_group": null,
    "gender": null,
    "rankings": [
      {
        "rank": 1,
        "book_id": 83,
        "book_title": "다중 주파수 멀티미디어 프로토콜",
        "book_author": "김채원",
        "purchase_count": 9,
        "average_rating": "4.00"
      },
      {
        "rank": 2,
        "book_id": 42,
        "book_title": "자가 이용 가능한 멀티 태스킹 인",
        "book_author": "최혜진",
        "purchase_count": 7,
        "average_rating": "4.00"
      }
    ]
  },
  "message": null
}
```

### 10. 세일 (Sales) - 2개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/sales/` | 타임 세일 생성 | Seller |
| POST | `/sales/{sale_id}/books` | 세일에 책 추가 | Seller |

**Request/Response 예시:**

```json
// POST /sales/ - Request
{
  "sale_name": "크리스마스 기념 할인",
  "discount_rate": 10,
  "started_at": "2025-12-14T13:12:32.323Z",
  "ended_at": "2025-12-25T23:59:59.999Z"
}

// POST /sales/ - Response (201)
{
  "status": "success",
  "data": {
    "id": 1,
    "sale_name": "크리스마스 기념 할인",
    "seller_id": 11,
    "discount_rate": "1.00",
    "started_at": "2025-12-14T13:12:32",
    "ended_at": "2025-12-14T13:12:52",
    "status": "INACTIVE",
    "created_at": "2025-12-14T22:15:11"
  },
  "message": "Sale created successfully"
}

// POST /sales/{sale_id}/books - Request
{
  "book_id": 102
}

// POST /sales/{sale_id}/books - Response (200)
{
  "status": "success",
  "data": {
    "id": 1,
    "sale_name": "크리스마스 기념 할인",
    "seller_id": 11,
    "discount_rate": "1.00",
    "started_at": "2025-12-14T13:12:32",
    "ended_at": "2025-12-14T13:12:52",
    "status": "INACTIVE",
    "created_at": "2025-12-14T22:15:11"
  },
  "message": "Book added to sale"
}
```

### 11. 관리자 (Admin) - 4개
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/admin/orders` | 전체 주문 현황 조회 | Admin |
| POST | `/admin/settlements/calculate` | 정산 데이터 생성 | Admin |
| GET | `/users/` | 전체 사용자 조회 | Admin |
| PATCH | `/users/{user_id}/role` | 사용자 권한 변경 | Admin |

**Request/Response 예시:**

```json
// GET /admin/orders?page=1&size=10 - Response (200)
{
  "status": "success",
  "data": {
    "orders": [
      {
        "id": 52,
        "user_id": 51,
        "order_date": "2025-12-14T21:51:58",
        "total_amount": "2500000.00",
        "status": "CREATED",
        "items": [...]
      }
    ],
    "total": 52,
    "page": 1,
    "size": 10
  },
  "message": null
}

// POST /admin/settlements/calculate - Response (200)
{
  "status": "success",
  "data": {
    "created_settlements": 10,
    "total_processed_orders": 94,
    "message": "Successfully created 10 settlements for 94 order items"
  },
  "message": "Successfully created 10 settlements for 94 order items"
}
```

---

## 응답 포맷

### 성공 응답
```json
{
  "status": "success",
  "data": { /* 실제 데이터 */ },
  "message": "Optional success message"
}
```

### 에러 응답
```json
{
  "timestamp": "2025-12-14T12:34:56",
  "path": "/api/endpoint",
  "status": 404,
  "code": "RESOURCE_NOT_FOUND",
  "message": "User not found",
  "details": null
}
```

---

## 인증 방식

### JWT Bearer Token
- **Access Token**: 30분 유효
- **Refresh Token**: 7일 유효

```http
Authorization: Bearer <access_token>
```

### 권한 레벨
1. **Public**: 인증 불필요
2. **User**: 일반 사용자 (is_active=true)
3. **Seller**: 판매자 등록 완료된 사용자
4. **Admin**: 관리자 권한

---

## 페이지네이션

목록 조회 엔드포인트는 페이지네이션을 지원합니다:

```http
GET /books/?page=1&size=10
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "books": [...],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

---

## 검색 및 필터링

### 도서 검색 예시
```http
GET /books/?keyword=파이썬&sort=price_asc&page=1&size=10
```

**Parameters:**
- `keyword`: 제목/저자/출판사 검색
- `sort`: 정렬 기준 (`price_asc`, `price_desc`, `created_at`, `purchase_count`, `average_rating`)
- `page`: 페이지 번호 (기본: 1)
- `size`: 페이지 크기 (기본: 10, 최대: 100)

---

## 에러 코드

| HTTP Status | Code | 설명 |
|-------------|------|------|
| 400 | CART_EMPTY | 장바구니가 비어있음 |
| 400 | ORDER_CANCEL_NOT_ALLOWED | 주문 취소 불가 |
| 401 | AUTH_UNAUTHORIZED | 인증되지 않은 요청 |
| 401 | AUTH_INVALID_CREDENTIALS | 잘못된 이메일 또는 비밀번호 |
| 403 | AUTH_FORBIDDEN | 권한 없음 |
| 403 | BOOK_NOT_OWNED | 본인 도서가 아님 |
| 403 | REVIEW_NOT_OWNED | 본인 리뷰가 아님 |
| 403 | REVIEW_NOT_ALLOWED | 리뷰 작성 불가 (미구매) |
| 404 | BOOK_NOT_FOUND | 도서를 찾을 수 없음 |
| 404 | FAVORITE_NOT_FOUND | 찜 항목을 찾을 수 없음 |
| 409 | USER_ALREADY_EXISTS | 이미 존재하는 사용자 |
| 409 | SELLER_ALREADY_EXISTS | 이미 판매자 등록됨 |
| 409 | BOOK_ALREADY_EXISTS | 중복된 ISBN |
| 409 | CART_ITEM_ALREADY_EXISTS | 이미 장바구니에 있음 |
| 409 | REVIEW_ALREADY_EXISTS | 이미 리뷰 작성함 |
| 409 | FAVORITE_ALREADY_EXISTS | 이미 찜한 도서 |
| 422 | VALIDATION_FAILED | 요청 데이터 검증 실패 |
| 500 | INTERNAL_SERVER_ERROR | 서버 내부 오류 |

---

## Rate Limiting

SlowAPI를 사용한 요청 제한:
- 기본: `100 requests/minute`
- IP 기반 제한

---

## 변경 이력

### v1.0.0
- 초기 API 설계 완료
- 36개 엔드포인트 구현
- JWT 인증 적용
- Redis 캐싱 적용 (랭킹)
- 테스트 109개 작성 (100% 통과)
