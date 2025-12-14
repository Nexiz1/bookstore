"""Cart repository module for database operations.

This module handles all database CRUD operations for shopping carts.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart


class CartRepository:
    """Repository for cart-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

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

    def create(self, cart_data: dict, *, commit: bool = False) -> Cart:
        """Create a new cart item.

        Args:
            cart_data: Dictionary containing cart fields.
            commit: If True, commit the transaction. Default False.

        Returns:
            Cart: Created cart instance.
        """
        db_cart = Cart(**cart_data)
        self.db.add(db_cart)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_cart)
        return db_cart

    def update_quantity(self, cart: Cart, quantity: int, *, commit: bool = False) -> Cart:
        """Update cart item quantity.

        Args:
            cart: Cart instance to update.
            quantity: New quantity value.
            commit: If True, commit the transaction. Default False.

        Returns:
            Cart: Updated cart instance.
        """
        cart.quantity = quantity
        if commit:
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def delete(self, cart: Cart, *, commit: bool = False) -> None:
        """Delete a cart item.

        Args:
            cart: Cart instance to delete.
            commit: If True, commit the transaction. Default False.
        """
        self.db.delete(cart)
        if commit:
            self.db.commit()

    def delete_multiple(self, carts: List[Cart], *, commit: bool = False) -> None:
        """Delete multiple cart items.

        Args:
            carts: List of Cart instances to delete.
            commit: If True, commit the transaction. Default False.
        """
        for cart in carts:
            self.db.delete(cart)
        if commit:
            self.db.commit()
