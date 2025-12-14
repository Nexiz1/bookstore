from sqlalchemy.orm import Session

from app.exceptions.order_exceptions import OrderItemNotFoundException
from app.exceptions.review_exceptions import (
    ReviewAlreadyExistsException,
    ReviewNotAllowedException,
    ReviewNotFoundException,
    ReviewNotOwnedException,
)
from app.repositories.book_repository import BookRepository
from app.repositories.order_repository import OrderItemRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewListResponse, ReviewResponse, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.book_repo = BookRepository(db)

    def create_review(
        self, user_id: int, book_id: int, review_data: ReviewCreate
    ) -> ReviewResponse:
        # 주문 아이템 확인 (구매한 책인지)
        order_item = self.order_item_repo.get_by_id(review_data.order_item_id)
        if not order_item:
            raise OrderItemNotFoundException()

        # 주문한 유저인지 확인
        if order_item.order.user_id != user_id:
            raise ReviewNotAllowedException()

        # 해당 책에 대한 주문인지 확인
        if order_item.book_id != book_id:
            raise ReviewNotAllowedException("This order item is not for this book")

        # 이미 리뷰가 있는지 확인
        existing_review = self.review_repo.get_by_order_item_id(
            review_data.order_item_id
        )
        if existing_review:
            raise ReviewAlreadyExistsException()

        # 리뷰 생성
        review = self.review_repo.create(
            {
                "user_id": user_id,
                "book_id": book_id,
                "order_item_id": review_data.order_item_id,
                "rating": review_data.rating,
                "comment": review_data.comment,
            }
        )

        # 책 평점 업데이트
        self._update_book_rating(book_id)

        # 리뷰 다시 조회 (user 정보 포함)
        review = self.review_repo.get_by_id(review.id)
        return self._build_review_response(review)

    def get_book_reviews(self, book_id: int) -> ReviewListResponse:
        reviews, total, avg_rating = self.review_repo.get_by_book_id(book_id)

        review_responses = [self._build_review_response(r) for r in reviews]

        return ReviewListResponse(
            reviews=review_responses, total=total, average_rating=avg_rating
        )

    def update_review(
        self, user_id: int, review_id: int, update_data: ReviewUpdate
    ) -> ReviewResponse:
        """리뷰 수정 (작성자 본인만 가능)"""
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException()

        # 본인 리뷰인지 확인
        if review.user_id != user_id:
            raise ReviewNotOwnedException()

        # 리뷰 업데이트
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_review = self.review_repo.update(review, update_dict)

        # 평점이 변경된 경우 책 평점 재계산
        if "rating" in update_dict:
            self._update_book_rating(review.book_id)

        # 리뷰 다시 조회 (user 정보 포함)
        updated_review = self.review_repo.get_by_id(review_id)
        return self._build_review_response(updated_review)

    def delete_review(
        self, user_id: int, review_id: int, is_admin: bool = False
    ) -> bool:
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException()

        # 본인 리뷰인지 확인 (관리자는 예외)
        if not is_admin and review.user_id != user_id:
            raise ReviewNotOwnedException()

        book_id = review.book_id
        self.review_repo.delete(review)

        # 책 평점 업데이트
        self._update_book_rating(book_id)

        return True

    def _update_book_rating(self, book_id: int):
        avg_rating, count = self.review_repo.get_average_rating(book_id)
        book = self.book_repo.get_by_id(book_id)
        self.book_repo.update_stats(book, rating=avg_rating, review_count=count)

    def _build_review_response(self, review) -> ReviewResponse:
        return ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.user.name if review.user else "Unknown",
            book_id=review.book_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )
