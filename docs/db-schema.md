# 데이터베이스 스키마

## ERD (Entity-Relationship Diagram)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │────────>│   Seller    │────────>│    Book     │
│             │  1:1    │             │  1:N    │             │
└──────┬──────┘         └─────────────┘         └──────┬──────┘
       │                                                 │
       │ 1:N                                            │ 1:N
       │                                                 │
       ▼                                                 ▼
┌─────────────┐                                  ┌─────────────┐
│    Cart     │                                  │   Review    │
│             │                                  │             │
└─────────────┘                                  └─────────────┘
       │                                                 │
       │                                                 │ N:1
       │ N:1                                            │
       │                                                 ▼
       │                                          ┌─────────────┐
       │                                          │  OrderItem  │
       │                                          │             │
       │                                          └──────┬──────┘
       │                                                 │ N:1
       │                                                 │
       ▼                                                 ▼
┌─────────────┐                                  ┌─────────────┐
│   Order     │<─────────────────────────────────│  OrderItem  │
│             │              1:N                 │             │
└──────┬──────┘                                  └──────┬──────┘
       │                                                 │
       │ 1:N                                            │ N:M
       │                                                 │
       ▼                                                 ▼
┌─────────────┐                                  ┌─────────────┐
│ Settlement  │                                  │ Settlement  │
│             │<─────────────────────────────────│   Order     │
└─────────────┘         N:M                      └─────────────┘

Additional Entities:
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Favorite   │         │   Ranking   │         │    Sale     │
│  (User-Book)│         │  (Book Top) │         │ (TimeSale)  │
└─────────────┘         └─────────────┘         └─────────────┘
```

## 테이블 정의

### 1. User (사용자)
```sql
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender ENUM('male', 'female') DEFAULT NULL,
    birth DATE DEFAULT NULL,
    address TEXT DEFAULT NULL,
    role ENUM('user', 'seller', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `role`: 권한 레벨 (user, seller, admin)
- `is_active`: 계정 활성화 상태
- `gender`, `birth`: 연령/성별 기반 랭킹용

### 2. Seller (판매자)
```sql
CREATE TABLE seller (
    id INT PRIMARY KEY AUTO_INCREMENT,
    userId INT UNIQUE NOT NULL,
    businessName VARCHAR(200) NOT NULL,
    businessNumber VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phoneNumber VARCHAR(20),
    payoutAccount VARCHAR(100) NOT NULL,
    payoutHolder VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (userId) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (userId),
    INDEX idx_business_number (businessNumber)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `businessNumber`: 사업자등록번호 (UNIQUE)
- `payoutAccount`, `payoutHolder`: 정산 계좌 정보

### 3. Book (도서)
```sql
CREATE TABLE book (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sellerId INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    summary TEXT,
    isbn VARCHAR(20) UNIQUE,
    price DECIMAL(19, 2) NOT NULL,
    status ENUM('ONSALE', 'SOLDOUT', 'DISCONTINUED') DEFAULT 'ONSALE',
    purchaseCount INT DEFAULT 0,
    reviewCount INT DEFAULT 0,
    averageRating DECIMAL(3, 2) DEFAULT 0.0,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (sellerId) REFERENCES seller(id) ON DELETE CASCADE,
    INDEX idx_seller_id (sellerId),
    INDEX idx_status (status),
    INDEX idx_purchase_count (purchaseCount DESC),
    INDEX idx_average_rating (averageRating DESC),
    FULLTEXT idx_search (title, author, publisher)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `purchaseCount`: 판매량 (랭킹용)
- `averageRating`: 평균 평점 (랭킹용)
- `status`: 판매 상태 (ONSALE, SOLDOUT, DISCONTINUED)

### 4. Cart (장바구니)
```sql
CREATE TABLE cart (
    id INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    bookId INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (userId) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (bookId) REFERENCES book(id) ON DELETE CASCADE,
    UNIQUE KEY uqUserBook (userId, bookId),
    CONSTRAINT check_cart_quantity CHECK (quantity >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5. Order (주문)
```sql
CREATE TABLE `order` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    totalAmount DECIMAL(19, 2) NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'SHIPPING', 'ARRIVED', 'CANCELLED') DEFAULT 'PENDING',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (userId) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (userId),
    INDEX idx_status (status),
    INDEX idx_created_at (createdAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `status`: 주문 상태 (PENDING → CONFIRMED → SHIPPING → ARRIVED)
- `totalAmount`: 주문 총액

### 6. OrderItem (주문 아이템)
```sql
CREATE TABLE orderItem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    orderId INT NOT NULL,
    bookId INT NOT NULL,
    price DECIMAL(19, 2) NOT NULL,
    totalAmount DECIMAL(19, 2) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    is_settled BOOLEAN DEFAULT FALSE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (orderId) REFERENCES `order`(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bookId) REFERENCES book(id),
    UNIQUE KEY uqOrderUserBook (orderId, bookId),
    CONSTRAINT check_order_item_quantity CHECK (quantity >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `is_settled`: 정산 완료 여부
- `price`: 주문 당시 가격 (스냅샷)

### 7. Review (리뷰)
```sql
CREATE TABLE review (
    id INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    bookId INT NOT NULL,
    orderItemId INT UNIQUE NOT NULL,
    rating INT NOT NULL,
    comment TEXT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (userId) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (bookId) REFERENCES book(id) ON DELETE CASCADE,
    FOREIGN KEY (orderItemId) REFERENCES orderItem(id) ON DELETE CASCADE,
    CONSTRAINT check_rating CHECK (rating >= 1 AND rating <= 5),
    INDEX idx_book_id (bookId),
    INDEX idx_user_id (userId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `orderItemId`: 구매 이력 연결 (구매자만 리뷰 작성 가능)
- `rating`: 1~5점

### 8. Favorite (찜하기)
```sql
CREATE TABLE favorite (
    id INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    bookId INT NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (userId) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (bookId) REFERENCES book(id) ON DELETE CASCADE,
    UNIQUE KEY uqUserBook (userId, bookId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 9. Ranking (랭킹)
```sql
CREATE TABLE ranking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rankingType ENUM('purchaseCount', 'averageRating') NOT NULL,
    rank INT NOT NULL,
    bookId INT NOT NULL,
    purchaseCount INT DEFAULT 0,
    averageRating DECIMAL(3, 2) DEFAULT 0.0,
    ageGroup VARCHAR(20) DEFAULT 'ALL',
    gender VARCHAR(10) DEFAULT 'ALL',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bookId) REFERENCES book(id) ON DELETE CASCADE,
    INDEX idx_ranking_type (rankingType),
    INDEX idx_age_gender (ageGroup, gender)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `rankingType`: 랭킹 타입 (판매량/평점)
- `ageGroup`, `gender`: 연령/성별별 랭킹 (현재는 'ALL')

### 10. Sale (타임 세일)
```sql
CREATE TABLE sale (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bookId INT NOT NULL,
    discountRate DECIMAL(5, 2) NOT NULL,
    startTime TIMESTAMP NOT NULL,
    endTime TIMESTAMP NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (bookId) REFERENCES book(id) ON DELETE CASCADE,
    INDEX idx_book_id (bookId),
    INDEX idx_time_range (startTime, endTime),
    CONSTRAINT check_discount_rate CHECK (discountRate >= 0 AND discountRate <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 11. Settlement (정산)
```sql
CREATE TABLE settlement (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sellerId INT NOT NULL,
    totalSales DECIMAL(19, 2) NOT NULL,
    commission DECIMAL(19, 2) NOT NULL,
    finalPayout DECIMAL(19, 2) NOT NULL,
    periodStart DATE NOT NULL,
    periodEnd DATE NOT NULL,
    settlementDate DATE NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sellerId) REFERENCES seller(id) ON DELETE CASCADE,
    INDEX idx_seller_id (sellerId),
    INDEX idx_settlement_date (settlementDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**주요 필드:**
- `commission`: 수수료 (10%)
- `finalPayout`: 최종 정산액 (매출 - 수수료)

### 12. SettlementOrder (정산-주문 매핑)
```sql
CREATE TABLE settlementOrder (
    id INT PRIMARY KEY AUTO_INCREMENT,
    settlementId INT NOT NULL,
    orderItemId INT NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (settlementId) REFERENCES settlement(id) ON DELETE CASCADE,
    FOREIGN KEY (orderItemId) REFERENCES orderItem(id) ON DELETE CASCADE,
    UNIQUE KEY uqSettlementOrderItem (settlementId, orderItemId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 주요 인덱스 전략

### 검색 최적화
- `book.title`, `book.author`, `book.publisher`: FULLTEXT 인덱스
- `user.email`: UNIQUE 인덱스

### 정렬 최적화
- `book.purchaseCount`: DESC 인덱스 (판매량 순 정렬)
- `book.averageRating`: DESC 인덱스 (평점 순 정렬)
- `order.createdAt`: 인덱스 (최신 주문 조회)

### 조인 최적화
- 모든 외래 키에 인덱스 설정

## 제약 조건 (Constraints)

### UNIQUE 제약
- `user.email`: 중복 이메일 방지
- `seller.businessNumber`: 중복 사업자등록번호 방지
- `cart(userId, bookId)`: 사용자당 동일 도서 1개만
- `review.orderItemId`: 주문 아이템당 리뷰 1개만

### CHECK 제약
- `review.rating`: 1~5 범위
- `cart.quantity`: >= 1
- `sale.discountRate`: 0~100% 범위

### CASCADE 설정
- `user` 삭제 시 → `cart`, `order`, `review`, `favorite` 모두 삭제
- `order` 삭제 시 → `orderItem` 삭제
- `seller` 삭제 시 → `book` 삭제

## 데이터 타입 선택

- **가격/금액**: `DECIMAL(19, 2)` - 정확한 소수점 연산
- **평점**: `DECIMAL(3, 2)` - 0.00 ~ 5.00
- **ENUM**: 고정된 상태값 (role, status)
- **TEXT**: 가변 길이 텍스트 (summary, comment, address)

## 초기 데이터 (시드 데이터)

시드 데이터 생성 스크립트: `scripts/seed.py`

**생성 데이터:**
- Admin 계정 1개
- 판매자 계정 3개
- 일반 사용자 5개
- 도서 20개
- 주문 10개
- 리뷰 15개

**실행:**
```bash
docker-compose exec app python scripts/seed.py
```

## 마이그레이션 이력

Alembic을 사용한 스키마 버전 관리:

```bash
# 현재 적용된 마이그레이션 확인
alembic current

# 마이그레이션 이력 확인
alembic history

# 특정 버전으로 이동
alembic upgrade <revision>
```
