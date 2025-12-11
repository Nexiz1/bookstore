from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.exceptions.book_exceptions import BookNotFoundException
from app.exceptions.cart_exceptions import (
    CartEmptyException,
    CartItemAlreadyExistsException,
    CartItemNotFoundException,
)
from app.repositories.book_repository import BookRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartCreate, CartItemResponse, CartListResponse, CartUpdate


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.book_repo = BookRepository(db)

    def get_my_cart(self, user_id: int) -> CartListResponse:
        cart_items = self.cart_repo.get_by_user_id(user_id)

        items = []
        total_amount = Decimal(0)

        for cart in cart_items:
            subtotal = cart.book.price * cart.quantity
            items.append(
                CartItemResponse(
                    id=cart.id,
                    book_id=cart.book_id,
                    book_title=cart.book.title,
                    book_price=cart.book.price,
                    quantity=cart.quantity,
                    subtotal=subtotal,
                    created_at=cart.created_at,
                )
            )
            total_amount += subtotal

        return CartListResponse(
            items=items, total_amount=total_amount, total_items=len(items)
        )

    def add_to_cart(self, user_id: int, cart_data: CartCreate) -> CartItemResponse:
        # 책 존재 확인
        book = self.book_repo.get_by_id(cart_data.book_id)
        if not book:
            raise BookNotFoundException()

        # 이미 장바구니에 있는지 확인
        existing_item = self.cart_repo.get_by_user_and_book(user_id, cart_data.book_id)
        if existing_item:
            raise CartItemAlreadyExistsException()

        cart_dict = {
            "user_id": user_id,
            "book_id": cart_data.book_id,
            "quantity": cart_data.quantity,
        }
        cart = self.cart_repo.create(cart_dict)

        # 책 정보 로드를 위해 다시 조회
        cart = self.cart_repo.get_by_id(cart.id)
        subtotal = cart.book.price * cart.quantity

        return CartItemResponse(
            id=cart.id,
            book_id=cart.book_id,
            book_title=cart.book.title,
            book_price=cart.book.price,
            quantity=cart.quantity,
            subtotal=subtotal,
            created_at=cart.created_at,
        )

    def update_quantity(
        self, user_id: int, cart_id: int, update_data: CartUpdate
    ) -> CartItemResponse:
        cart = self.cart_repo.get_by_id(cart_id)
        if not cart or cart.user_id != user_id:
            raise CartItemNotFoundException()

        cart = self.cart_repo.update_quantity(cart, update_data.quantity)
        subtotal = cart.book.price * cart.quantity

        return CartItemResponse(
            id=cart.id,
            book_id=cart.book_id,
            book_title=cart.book.title,
            book_price=cart.book.price,
            quantity=cart.quantity,
            subtotal=subtotal,
            created_at=cart.created_at,
        )

    def remove_from_cart(self, user_id: int, cart_id: int) -> bool:
        cart = self.cart_repo.get_by_id(cart_id)
        if not cart or cart.user_id != user_id:
            raise CartItemNotFoundException()

        self.cart_repo.delete(cart)
        return True
