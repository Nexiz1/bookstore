from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        return (
            self.db.query(Cart)
            .options(joinedload(Cart.book))
            .filter(Cart.id == cart_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> List[Cart]:
        return (
            self.db.query(Cart)
            .options(joinedload(Cart.book))
            .filter(Cart.user_id == user_id)
            .all()
        )

    def get_by_user_and_book(self, user_id: int, book_id: int) -> Optional[Cart]:
        return (
            self.db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.book_id == book_id)
            .first()
        )

    def get_by_ids(self, cart_ids: List[int], user_id: int) -> List[Cart]:
        return (
            self.db.query(Cart)
            .options(joinedload(Cart.book))
            .filter(Cart.id.in_(cart_ids), Cart.user_id == user_id)
            .all()
        )

    def create(self, cart_data: dict) -> Cart:
        db_cart = Cart(**cart_data)
        self.db.add(db_cart)
        self.db.commit()
        self.db.refresh(db_cart)
        return db_cart

    def update_quantity(self, cart: Cart, quantity: int) -> Cart:
        cart.quantity = quantity
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def delete(self, cart: Cart) -> None:
        self.db.delete(cart)
        self.db.commit()

    def delete_multiple(self, carts: List[Cart]) -> None:
        for cart in carts:
            self.db.delete(cart)
        self.db.commit()
