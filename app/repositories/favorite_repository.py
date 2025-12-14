"""Favorite repository module for database operations.

This module handles all database CRUD operations for favorites.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.favorite import Favorite


class FavoriteRepository:
    """Repository for favorite-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, favorite_id: int) -> Optional[Favorite]:
        return self.db.query(Favorite).filter(Favorite.id == favorite_id).first()

    def get_by_user_and_book(self, user_id: int, book_id: int) -> Optional[Favorite]:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.book_id == book_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> List[Favorite]:
        return (
            self.db.query(Favorite)
            .options(joinedload(Favorite.book))
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def create(self, favorite_data: dict, *, commit: bool = True) -> Favorite:
        """Create a new favorite.

        Args:
            favorite_data: Dictionary containing favorite fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            Favorite: Created favorite instance.
        """
        db_favorite = Favorite(**favorite_data)
        self.db.add(db_favorite)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_favorite)
        return db_favorite

    def delete(self, favorite: Favorite, *, commit: bool = True) -> None:
        """Delete a favorite.

        Args:
            favorite: Favorite instance to delete.
            commit: If True, commit the transaction. Default True.
        """
        self.db.delete(favorite)
        if commit:
            self.db.commit()
