from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.favorite import Favorite


class FavoriteRepository:
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

    def create(self, favorite_data: dict) -> Favorite:
        db_favorite = Favorite(**favorite_data)
        self.db.add(db_favorite)
        self.db.commit()
        self.db.refresh(db_favorite)
        return db_favorite

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()
