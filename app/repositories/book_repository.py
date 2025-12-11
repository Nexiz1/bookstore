"""Book repository module for database operations."""

from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookSortBy


class BookRepository:
    """Repository for book-related database operations.

    This class handles all database CRUD operations and queries for books.

    Attributes:
        db: SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        sort: BookSortBy = BookSortBy.DATE_DESC,
        seller_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Book], int]:
        query = self.db.query(Book)

        # 키워드 검색 (제목, 저자, 출판사)
        if keyword:
            query = query.filter(
                or_(
                    Book.title.ilike(f"%{keyword}%"),
                    Book.author.ilike(f"%{keyword}%"),
                    Book.publisher.ilike(f"%{keyword}%"),
                )
            )

        # 판매자 필터
        if seller_id:
            query = query.filter(Book.seller_id == seller_id)

        # 상태 필터
        if status:
            query = query.filter(Book.status == status)

        # 정렬
        if sort == BookSortBy.PRICE_ASC:
            query = query.order_by(asc(Book.price))
        elif sort == BookSortBy.PRICE_DESC:
            query = query.order_by(desc(Book.price))
        elif sort == BookSortBy.DATE_ASC:
            query = query.order_by(asc(Book.created_at))
        elif sort == BookSortBy.DATE_DESC:
            query = query.order_by(desc(Book.created_at))
        elif sort == BookSortBy.RATING:
            query = query.order_by(desc(Book.average_rating))
        elif sort == BookSortBy.SALES:
            query = query.order_by(desc(Book.purchase_count))

        total = query.count()
        books = query.offset(skip).limit(limit).all()
        return books, total

    def create(self, book_data: dict) -> Book:
        db_book = Book(**book_data)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def update(self, book: Book, update_data: dict) -> Book:
        for key, value in update_data.items():
            if value is not None:
                setattr(book, key, value)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update_stats(
        self,
        book: Book,
        rating: float = None,
        review_count: int = None,
        purchase_count: int = None,
    ) -> Book:
        if rating is not None:
            book.average_rating = rating
        if review_count is not None:
            book.review_count = review_count
        if purchase_count is not None:
            book.purchase_count = purchase_count
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        book.status = "SOLDOUT"
        self.db.commit()
