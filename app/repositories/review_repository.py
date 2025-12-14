"""Review repository module for database operations.

This module handles all database CRUD operations for reviews.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.review import Review


class ReviewRepository:
    """Repository for review-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

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

    def create(self, review_data: dict, *, commit: bool = True) -> Review:
        """Create a new review.

        Args:
            review_data: Dictionary containing review fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            Review: Created review instance.
        """
        db_review = Review(**review_data)
        self.db.add(db_review)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_review)
        return db_review

    def update(self, review: Review, update_data: dict, *, commit: bool = True) -> Review:
        """Update a review.

        Args:
            review: Review instance to update.
            update_data: Dictionary of fields to update.
            commit: If True, commit the transaction. Default True.

        Returns:
            Review: Updated review instance.
        """
        for key, value in update_data.items():
            if value is not None:
                setattr(review, key, value)
        if commit:
            self.db.commit()
            self.db.refresh(review)
        return review

    def delete(self, review: Review, *, commit: bool = True) -> None:
        """Delete a review.

        Args:
            review: Review instance to delete.
            commit: If True, commit the transaction. Default True.
        """
        self.db.delete(review)
        if commit:
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
