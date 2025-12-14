from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions.book_exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    BookNotOwnedException,
)
from app.exceptions.seller_exceptions import SellerNotFoundException
from app.repositories.book_repository import BookRepository
from app.repositories.seller_repository import SellerRepository
from app.schemas.book import (
    BookCreate,
    BookListResponse,
    BookResponse,
    BookSortBy,
    BookUpdate,
)


class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.book_repo = BookRepository(db)
        self.seller_repo = SellerRepository(db)

    def create_book(self, user_id: int, book_data: BookCreate) -> BookResponse:
        # 판매자 프로필 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException(
                "Seller profile not found. Please register as a seller first."
            )

        # ISBN 중복 확인
        existing_book = self.book_repo.get_by_isbn(book_data.isbn)
        if existing_book:
            raise BookAlreadyExistsException()

        book_dict = book_data.model_dump()
        book_dict["seller_id"] = seller.id

        book = self.book_repo.create(book_dict, commit=True)
        return book

    def get_books(
        self,
        page: int = 1,
        size: int = 10,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        sort: BookSortBy = BookSortBy.DATE_DESC,
    ) -> BookListResponse:
        skip = (page - 1) * size
        books, total = self.book_repo.get_all(
            skip=skip,
            limit=size,
            keyword=keyword,
            category=category,
            sort=sort,
            status="ONSALE",  # 판매 중인 책만 조회
        )
        return BookListResponse(
            books=[BookResponse.model_validate(b) for b in books],
            total=total,
            page=page,
            size=size,
        )

    def get_book(self, book_id: int) -> BookResponse:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException()
        return book

    def update_book(
        self, user_id: int, book_id: int, update_data: BookUpdate
    ) -> BookResponse:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException()

        # 본인 책인지 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller or book.seller_id != seller.id:
            raise BookNotOwnedException()

        update_dict = update_data.model_dump(exclude_unset=True)
        updated_book = self.book_repo.update(book, update_dict)
        return updated_book

    def delete_book(self, user_id: int, book_id: int) -> bool:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException()

        # 본인 책인지 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller or book.seller_id != seller.id:
            raise BookNotOwnedException()

        # 상태를 SOLDOUT으로 변경 (실제 삭제 아님)
        self.book_repo.delete(book)
        return True
