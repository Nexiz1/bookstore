from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_order_item_id(self, order_item_id: int) -> Optional[Review]:
        return (
            self.db.query(Review).filter(Review.order_item_id == order_item_id).first()
        )

    def get_by_book_id(self, book_id: int) -> Tuple[List[Review], int, float]:
        query = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.book_id == book_id)
        )
        reviews = query.order_by(Review.created_at.desc()).all()
        total = len(reviews)

        # 평균 평점 계산
        avg_rating = (
            self.db.query(func.avg(Review.rating))
            .filter(Review.book_id == book_id)
            .scalar()
            or 0
        )
        return reviews, total, float(avg_rating)

    def create(self, review_data: dict) -> Review:
        db_review = Review(**review_data)
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def delete(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()

    def get_average_rating(self, book_id: int) -> Tuple[float, int]:
        avg = (
            self.db.query(func.avg(Review.rating))
            .filter(Review.book_id == book_id)
            .scalar()
            or 0
        )
        count = self.db.query(Review).filter(Review.book_id == book_id).count()
        return float(avg), count
