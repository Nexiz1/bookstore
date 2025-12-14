# API 설계 문서

## 개요
BookStore API는 RESTful 설계 원칙을 따르며, FastAPI 프레임워크를 사용하여 구현되었습니다.

## 엔드포인트 목록

### 1. 인증 (Authentication)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/auth/signup` | 회원가입 | Public |
| POST | `/auth/login` | 로그인 (JWT 발급) | Public |
| POST | `/auth/refresh` | Access Token 재발급 | Public |
| POST | `/auth/logout` | 로그아웃 | User |

### 2. 사용자 (Users)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/users/me` | 내 프로필 조회 | User |
| PATCH | `/users/me` | 내 프로필 수정 | User |
| PATCH | `/users/me/password` | 비밀번호 변경 | User |
| GET | `/users/` | 전체 사용자 조회 | Admin |
| PATCH | `/users/{user_id}/role` | 사용자 권한 변경 | Admin |
| PATCH | `/users/{user_id}/deactivate` | 사용자 비활성화 | Admin |

### 3. 판매자 (Sellers)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/sellers/` | 판매자 등록 신청 | User |
| GET | `/sellers/me` | 내 판매자 정보 조회 | Seller |
| PATCH | `/sellers/me` | 내 판매자 정보 수정 | Seller |
| GET | `/sellers/settlements` | 내 정산 내역 조회 | Seller |

### 4. 도서 (Books)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/books/` | 도서 등록 | Seller |
| GET | `/books/` | 도서 목록 조회 (검색/필터) | Public |
| GET | `/books/{book_id}` | 도서 상세 조회 | Public |
| PATCH | `/books/{book_id}` | 도서 정보 수정 | Seller (본인) |
| DELETE | `/books/{book_id}` | 도서 삭제 | Seller (본인) |

### 5. 장바구니 (Carts)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/carts/` | 내 장바구니 조회 | User |
| POST | `/carts/` | 장바구니에 추가 | User |
| PATCH | `/carts/{cart_id}` | 장바구니 수량 변경 | User |
| DELETE | `/carts/{cart_id}` | 장바구니에서 제거 | User |

### 6. 주문 (Orders)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/orders/` | 주문 생성 (장바구니 → 주문) | User |
| GET | `/orders/` | 내 주문 목록 조회 | User |
| GET | `/orders/{order_id}` | 주문 상세 조회 | User (본인) |
| DELETE | `/orders/{order_id}` | 주문 취소 | User (본인) |

### 7. 리뷰 (Reviews)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/books/{book_id}/reviews` | 리뷰 작성 (구매자만) | User |
| GET | `/books/{book_id}/reviews` | 도서 리뷰 목록 조회 | Public |
| PATCH | `/books/{book_id}/reviews/{review_id}` | 리뷰 수정 | User (본인) |
| PATCH | `/reviews/{review_id}` | 리뷰 수정 (레거시) | User (본인) |
| DELETE | `/reviews/{review_id}` | 리뷰 삭제 | User (본인) or Admin |

### 8. 찜하기 (Favorites)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/favorites/` | 찜 추가 | User |
| GET | `/favorites/` | 내 찜 목록 조회 | User |
| DELETE | `/favorites/{book_id}` | 찜 취소 | User |

### 9. 랭킹 (Rankings)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/rankings/` | 도서 랭킹 조회 (Redis 캐시) | Public |

**Query Parameters:**
- `type`: `purchaseCount` (판매량) or `averageRating` (평점)
- `limit`: 결과 개수 (기본: 10)

### 10. 세일 (Sales)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/sales/` | 타임 세일 생성 | Seller |
| GET | `/sales/` | 진행 중인 세일 조회 | Public |
| GET | `/sales/{sale_id}` | 세일 상세 조회 | Public |
| PATCH | `/sales/{sale_id}` | 세일 수정 | Seller (본인) |
| DELETE | `/sales/{sale_id}` | 세일 삭제 | Seller (본인) |

### 11. 관리자 (Admin)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/admin/orders` | 전체 주문 현황 조회 | Admin |
| POST | `/admin/settlements/calculate` | 정산 데이터 생성 | Admin |

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

## 인증 방식

### JWT Bearer Token
- **Access Token**: 15분 유효
- **Refresh Token**: 7일 유효

```http
Authorization: Bearer <access_token>
```

### 권한 레벨
1. **Public**: 인증 불필요
2. **User**: 일반 사용자 (is_active=true)
3. **Seller**: 판매자 등록 완료된 사용자
4. **Admin**: 관리자 권한

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

## 검색 및 필터링

### 도서 검색 예시
```http
GET /books/?keyword=파이썬&sort=price&order=asc&min_price=10000&max_price=50000
```

**Parameters:**
- `keyword`: 제목/저자/출판사 검색
- `sort`: 정렬 기준 (`price`, `createdAt`, `purchaseCount`, `averageRating`)
- `order`: 정렬 방향 (`asc`, `desc`)
- `min_price`, `max_price`: 가격 범위

## 에러 코드

| HTTP Status | Code | 설명 |
|-------------|------|------|
| 400 | VALIDATION_ERROR | 요청 데이터 검증 실패 |
| 401 | UNAUTHORIZED | 인증되지 않은 요청 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | RESOURCE_NOT_FOUND | 리소스를 찾을 수 없음 |
| 409 | CONFLICT | 중복된 데이터 |
| 422 | UNPROCESSABLE_ENTITY | 처리할 수 없는 요청 |
| 500 | INTERNAL_SERVER_ERROR | 서버 내부 오류 |

## Rate Limiting

SlowAPI를 사용한 요청 제한:
- 기본: `100 requests/minute`
- IP 기반 제한

## 변경 이력

### v1.0.0
- 초기 API 설계 완료
- 40개 엔드포인트 구현
- JWT 인증 적용
- Redis 캐싱 적용 (랭킹)
- 테스트 109개 작성 (100% 통과)
