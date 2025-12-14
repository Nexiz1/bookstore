"""시드 데이터 생성 스크립트

faker 라이브러리를 사용하여 테스트용 더미 데이터를 생성합니다.
최소 200건 이상의 데이터가 생성됩니다.

실행 방법:
    python -m scripts.seed

또는 프로젝트 루트에서:
    python scripts/seed.py
"""

import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from faker import Faker

from app.core.database import Base, engine, get_db_context
from app.core.security import get_password_hash
from app.models.book import Book
from app.models.cart import Cart
from app.models.favorite import Favorite
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.seller_profile import SellerProfile
from app.models.user import User

# Faker 인스턴스 (한국어 지원)
fake = Faker("ko_KR")
Faker.seed(42)  # 재현 가능한 결과를 위한 시드 설정
random.seed(42)


def clear_all_data(db):
    """기존 데이터 모두 삭제 (외래 키 순서 고려)"""
    print("기존 데이터 삭제 중...")

    # 외래 키 의존성을 고려한 삭제 순서
    db.query(Review).delete()
    db.query(Cart).delete()
    db.query(Favorite).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Book).delete()
    db.query(SellerProfile).delete()
    db.query(User).delete()

    db.commit()
    print("기존 데이터 삭제 완료")


def create_users(db, count: int = 50) -> list[User]:
    """일반 사용자 생성"""
    print(f"사용자 {count}명 생성 중...")
    users = []

    # Admin 사용자 1명
    admin = User(
        role="admin",
        email="admin@bookstore.com",
        password=get_password_hash("admin123!"),
        name="관리자",
        birth_date=date(1990, 1, 1),
        gender="남성",
        address="서울시 강남구 테헤란로 123",
        phone_number="010-1234-5678",
    )
    db.add(admin)
    users.append(admin)

    # 일반 사용자 생성
    genders = ["남성", "여성"]
    for i in range(count - 1):
        user = User(
            role="user",
            email=f"user{i+1}@{fake.free_email_domain()}",
            password=get_password_hash("password123!"),
            name=fake.name(),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=70),
            gender=random.choice(genders),
            address=fake.address(),
            phone_number=fake.phone_number(),
        )
        db.add(user)
        users.append(user)

    db.flush()
    print(f"사용자 {len(users)}명 생성 완료")
    return users


def create_sellers(db, users: list[User], count: int = 10) -> list[SellerProfile]:
    """판매자 프로필 생성 (일부 사용자를 판매자로 전환)"""
    print(f"판매자 {count}명 생성 중...")
    sellers = []

    # 일부 사용자를 seller로 변경
    seller_users = random.sample(users[1:], min(count, len(users) - 1))  # admin 제외

    for i, user in enumerate(seller_users):
        user.role = "seller"

        seller = SellerProfile(
            user_id=user.id,
            business_name=f"{fake.company()} 북스",
            business_number=f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}",
            email=f"seller{i+1}@{fake.free_email_domain()}",
            gender=user.gender,
            address=fake.address(),
            phone_number=fake.phone_number(),
            payout_account=f"{random.randint(100000000000, 999999999999)}",
            payout_holder=user.name,
        )
        db.add(seller)
        sellers.append(seller)

    db.flush()
    print(f"판매자 {len(sellers)}명 생성 완료")
    return sellers


def create_books(db, sellers: list[SellerProfile], count: int = 100) -> list[Book]:
    """도서 생성"""
    print(f"도서 {count}권 생성 중...")
    books = []

    categories = [
        "소설", "에세이", "자기계발", "경제/경영", "인문학",
        "과학", "역사", "여행", "요리", "건강",
        "IT/컴퓨터", "예술", "만화", "아동", "외국어"
    ]

    publishers = [
        "민음사", "문학동네", "창비", "위즈덤하우스", "김영사",
        "시공사", "한빛미디어", "길벗", "을유문화사", "열린책들"
    ]

    statuses = ["ONSALE", "ONSALE", "ONSALE", "SOLDOUT", "TOBESOLD"]

    for i in range(count):
        seller = random.choice(sellers)
        category = random.choice(categories)

        book = Book(
            seller_id=seller.id,
            status=random.choice(statuses),
            title=f"{fake.catch_phrase()[:18]}",  # 최대 20자
            author=fake.name()[:18],
            publisher=random.choice(publishers)[:18],
            summary=fake.paragraph(nb_sentences=3)[:100],
            isbn=f"978{random.randint(1000000000, 9999999999)}"[:15],
            price=Decimal(random.randint(10, 50) * 1000),
            publication_date=fake.date_between(start_date="-5y", end_date="today"),
            average_rating=Decimal(str(round(random.uniform(3.0, 5.0), 2))),
            review_count=0,
            purchase_count=0,
        )
        db.add(book)
        books.append(book)

    db.flush()
    print(f"도서 {len(books)}권 생성 완료")
    return books


def create_orders(
    db,
    users: list[User],
    books: list[Book],
    order_count: int = 50
) -> tuple[list[Order], list[OrderItem]]:
    """주문 및 주문 항목 생성"""
    print(f"주문 {order_count}건 생성 중...")
    orders = []
    order_items = []

    # seller가 아닌 일반 사용자들만 주문 가능
    regular_users = [u for u in users if u.role in ("user", "admin")]

    order_statuses = ["CREATED", "SHIPPED", "ARRIVED", "ARRIVED", "ARRIVED"]

    for _ in range(order_count):
        user = random.choice(regular_users)

        # 1~5개 항목 주문
        num_items = random.randint(1, 5)
        selected_books = random.sample(books, min(num_items, len(books)))

        total_amount = Decimal(0)
        order_date = fake.date_time_between(start_date="-1y", end_date="now")

        order = Order(
            user_id=user.id,
            order_date=order_date,
            total_amount=Decimal(0),  # 임시 값, 나중에 업데이트
            status=random.choice(order_statuses),
        )
        db.add(order)
        db.flush()  # order.id 가져오기

        for book in selected_books:
            quantity = random.randint(1, 3)
            price = book.price
            item_total = price * quantity
            total_amount += item_total

            order_item = OrderItem(
                order_id=order.id,
                book_id=book.id,
                price=price,
                total_amount=item_total,
                quantity=quantity,
            )
            db.add(order_item)
            order_items.append(order_item)

            # 도서 구매 수 업데이트
            book.purchase_count += quantity

        order.total_amount = total_amount
        orders.append(order)

    db.flush()
    print(f"주문 {len(orders)}건, 주문 항목 {len(order_items)}건 생성 완료")
    return orders, order_items


def create_reviews(
    db,
    users: list[User],
    order_items: list[OrderItem],
    review_percentage: float = 0.3
) -> list[Review]:
    """리뷰 생성 (완료된 주문 항목에 대해)"""
    # ARRIVED 상태인 주문의 항목만 리뷰 가능
    reviewable_items = [
        oi for oi in order_items
        if oi.order.status == "ARRIVED"
    ]

    review_count = int(len(reviewable_items) * review_percentage)
    print(f"리뷰 {review_count}건 생성 중...")

    reviews = []
    reviewed_items = random.sample(reviewable_items, min(review_count, len(reviewable_items)))

    positive_comments = [
        "정말 재미있게 읽었습니다!",
        "기대 이상이었어요. 강력 추천합니다.",
        "내용이 알차고 유익합니다.",
        "감동적인 이야기였습니다.",
        "배송도 빠르고 책 상태도 좋았어요.",
    ]

    neutral_comments = [
        "괜찮은 책입니다.",
        "무난하게 읽을 만합니다.",
        "기대했던 것과는 조금 달랐어요.",
        "보통 수준의 책입니다.",
    ]

    negative_comments = [
        "기대에 못 미쳤습니다.",
        "내용이 좀 지루했어요.",
    ]

    for item in reviewed_items:
        rating = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]

        if rating >= 4:
            comment = random.choice(positive_comments)
        elif rating == 3:
            comment = random.choice(neutral_comments)
        else:
            comment = random.choice(negative_comments)

        review = Review(
            user_id=item.order.user_id,
            order_item_id=item.id,
            book_id=item.book_id,
            rating=rating,
            comment=comment,
        )
        db.add(review)
        reviews.append(review)

        # 도서 리뷰 수 및 평균 평점 업데이트
        book = item.book
        book.review_count += 1
        # 간단한 평균 계산 (정확한 계산을 위해서는 모든 리뷰를 조회해야 함)
        current_total = float(book.average_rating) * (book.review_count - 1)
        new_average = (current_total + rating) / book.review_count
        book.average_rating = Decimal(str(round(new_average, 2)))

    db.flush()
    print(f"리뷰 {len(reviews)}건 생성 완료")
    return reviews


def create_carts(db, users: list[User], books: list[Book], count: int = 30) -> list[Cart]:
    """장바구니 항목 생성"""
    print(f"장바구니 항목 {count}건 생성 중...")
    carts = []

    regular_users = [u for u in users if u.role in ("user", "admin")]
    onsale_books = [b for b in books if b.status == "ONSALE"]

    # 중복 방지를 위한 집합
    cart_combinations = set()

    for _ in range(count):
        attempts = 0
        while attempts < 100:
            user = random.choice(regular_users)
            book = random.choice(onsale_books)
            key = (user.id, book.id)

            if key not in cart_combinations:
                cart_combinations.add(key)
                cart = Cart(
                    user_id=user.id,
                    book_id=book.id,
                    quantity=random.randint(1, 3),
                )
                db.add(cart)
                carts.append(cart)
                break

            attempts += 1

    db.flush()
    print(f"장바구니 항목 {len(carts)}건 생성 완료")
    return carts


def create_favorites(db, users: list[User], books: list[Book], count: int = 50) -> list[Favorite]:
    """찜하기 항목 생성"""
    print(f"찜하기 항목 {count}건 생성 중...")
    favorites = []

    # 중복 방지를 위한 집합
    favorite_combinations = set()

    for _ in range(count):
        attempts = 0
        while attempts < 100:
            user = random.choice(users)
            book = random.choice(books)
            key = (user.id, book.id)

            if key not in favorite_combinations:
                favorite_combinations.add(key)
                favorite = Favorite(
                    user_id=user.id,
                    book_id=book.id,
                )
                db.add(favorite)
                favorites.append(favorite)
                break

            attempts += 1

    db.flush()
    print(f"찜하기 항목 {len(favorites)}건 생성 완료")
    return favorites


def main():
    """시드 데이터 생성 메인 함수"""
    print("=" * 60)
    print("BookStore 시드 데이터 생성 시작")
    print("=" * 60)

    # 테이블 생성 확인
    Base.metadata.create_all(bind=engine)

    with get_db_context() as db:
        try:
            # 1. 기존 데이터 삭제
            clear_all_data(db)

            # 2. 사용자 생성 (50명)
            users = create_users(db, count=50)

            # 3. 판매자 생성 (10명)
            sellers = create_sellers(db, users, count=10)

            # 4. 도서 생성 (100권)
            books = create_books(db, sellers, count=100)

            # 5. 주문 생성 (50건)
            orders, order_items = create_orders(db, users, books, order_count=50)

            # 6. 리뷰 생성 (주문 항목의 30%)
            reviews = create_reviews(db, users, order_items, review_percentage=0.3)

            # 7. 장바구니 생성 (30건)
            carts = create_carts(db, users, books, count=30)

            # 8. 찜하기 생성 (50건)
            favorites = create_favorites(db, users, books, count=50)

            # 최종 커밋
            db.commit()

            # 통계 출력
            print("\n" + "=" * 60)
            print("시드 데이터 생성 완료!")
            print("=" * 60)
            print(f"  - 사용자: {len(users)}명 (Admin 1명, Seller {len(sellers)}명, User {len(users) - len(sellers) - 1}명)")
            print(f"  - 판매자: {len(sellers)}명")
            print(f"  - 도서: {len(books)}권")
            print(f"  - 주문: {len(orders)}건")
            print(f"  - 주문 항목: {len(order_items)}건")
            print(f"  - 리뷰: {len(reviews)}건")
            print(f"  - 장바구니: {len(carts)}건")
            print(f"  - 찜하기: {len(favorites)}건")
            print("-" * 60)
            total = (len(users) + len(sellers) + len(books) + len(orders) +
                     len(order_items) + len(reviews) + len(carts) + len(favorites))
            print(f"  총 데이터: {total}건")
            print("=" * 60)

            print("\n테스트 계정 정보:")
            print("  - Admin: admin@bookstore.com / admin123!")
            print("  - User: user1@xxx.com ~ user49@xxx.com / password123!")

        except Exception as e:
            db.rollback()
            print(f"\n오류 발생: {e}")
            raise


if __name__ == "__main__":
    main()
