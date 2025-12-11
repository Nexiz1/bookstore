from sqlalchemy.orm import Session

from app.exceptions.book_exceptions import BookNotFoundException
from app.exceptions.favorite_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteNotFoundException,
)
from app.repositories.book_repository import BookRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.schemas.favorite import FavoriteBookResponse, FavoriteListResponse


class FavoriteService:
    def __init__(self, db: Session):
        self.db = db
        self.favorite_repo = FavoriteRepository(db)
        self.book_repo = BookRepository(db)

    def add_favorite(self, user_id: int, book_id: int) -> FavoriteBookResponse:
        # 책 존재 확인
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException()

        # 이미 찜했는지 확인
        existing = self.favorite_repo.get_by_user_and_book(user_id, book_id)
        if existing:
            raise FavoriteAlreadyExistsException()

        favorite = self.favorite_repo.create({"user_id": user_id, "book_id": book_id})

        return FavoriteBookResponse(
            id=favorite.id,
            book_id=book.id,
            book_title=book.title,
            book_author=book.author,
            book_price=book.price,
            created_at=favorite.created_at,
        )

    def remove_favorite(self, user_id: int, book_id: int) -> bool:
        favorite = self.favorite_repo.get_by_user_and_book(user_id, book_id)
        if not favorite:
            raise FavoriteNotFoundException()

        self.favorite_repo.delete(favorite)
        return True

    def get_my_favorites(self, user_id: int) -> FavoriteListResponse:
        favorites = self.favorite_repo.get_by_user_id(user_id)

        favorite_responses = []
        for fav in favorites:
            favorite_responses.append(
                FavoriteBookResponse(
                    id=fav.id,
                    book_id=fav.book_id,
                    book_title=fav.book.title,
                    book_author=fav.book.author,
                    book_price=fav.book.price,
                    created_at=fav.created_at,
                )
            )

        return FavoriteListResponse(
            favorites=favorite_responses, total=len(favorite_responses)
        )
