"""Order service module for business logic.

This module handles all order-related business logic with proper
transaction management using the Unit of Work pattern.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.database import UnitOfWork
from app.exceptions.cart_exceptions import CartEmptyException
from app.exceptions.order_exceptions import (
    OrderCancelNotAllowedException,
    OrderNotFoundException,
)
from app.repositories.book_repository import BookRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderItemRepository, OrderRepository
from app.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
)


class OrderService:
    """Service for order-related business logic.

    This service manages transactions to ensure atomicity across
    multiple repository operations (order creation, item addition,
    book stats update, cart clearing).
    """

    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.cart_repo = CartRepository(db)
        self.book_repo = BookRepository(db)

    def create_order(self, user_id: int, order_data: OrderCreate) -> OrderResponse:
        """Create a new order from cart items.

        This method ensures atomicity - all operations succeed together
        or fail together (rollback on any error).

        Transaction includes:
        1. Create order record
        2. Create order items for each cart item
        3. Update book purchase counts
        4. Clear cart items

        Args:
            user_id: ID of the user creating the order.
            order_data: Order creation data with optional cart_item_ids.

        Returns:
            OrderResponse: Created order with items.

        Raises:
            CartEmptyException: If no items to order.
        """
        # 장바구니 아이템 조회
        if order_data.cart_item_ids:
            cart_items = self.cart_repo.get_by_ids(order_data.cart_item_ids, user_id)
        else:
            cart_items = self.cart_repo.get_by_user_id(user_id)

        if not cart_items:
            raise CartEmptyException("No items to order")

        # 총액 계산
        total_amount = Decimal(0)
        for cart in cart_items:
            total_amount += cart.book.price * cart.quantity

        # Unit of Work 패턴으로 트랜잭션 관리
        with UnitOfWork(self.db) as uow:
            try:
                # 1. 주문 생성 (commit=False)
                order = self.order_repo.create(
                    {"user_id": user_id, "total_amount": total_amount, "status": "CREATED"}
                )

                # 2. 주문 아이템 생성 (commit=False)
                order_items = []
                for cart in cart_items:
                    item_total = cart.book.price * cart.quantity
                    order_item = self.order_repo.add_item(
                        {
                            "order_id": order.id,
                            "book_id": cart.book_id,
                            "price": cart.book.price,
                            "total_amount": item_total,
                            "quantity": cart.quantity,
                        }
                    )
                    order_items.append(order_item)

                    # 3. 책 판매량 증가 (commit=False)
                    book = self.book_repo.get_by_id(cart.book_id)
                    if book:
                        self.book_repo.update_stats(
                            book, purchase_count=book.purchase_count + cart.quantity
                        )

                # 4. 장바구니 비우기 (commit=False)
                self.cart_repo.delete_multiple(cart_items)

                # 모든 작업 성공 시 한 번에 커밋
                uow.commit()

                # refresh를 위해 다시 조회
                self.db.refresh(order)
                for item in order_items:
                    self.db.refresh(item)

            except Exception:
                # 예외 발생 시 자동으로 롤백됨 (UnitOfWork.__exit__)
                raise

        return self._build_order_response(order, order_items)

    def get_my_orders(
        self, user_id: int, page: int = 1, size: int = 10
    ) -> OrderListResponse:
        """Get orders for a specific user with pagination."""
        skip = (page - 1) * size
        orders, total = self.order_repo.get_by_user_id(user_id, skip=skip, limit=size)

        order_responses = []
        for order in orders:
            order_responses.append(self._build_order_response(order, order.items))

        return OrderListResponse(
            orders=order_responses, total=total, page=page, size=size
        )

    def get_order(self, user_id: int, order_id: int) -> OrderResponse:
        """Get a specific order by ID."""
        order = self.order_repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundException()

        return self._build_order_response(order, order.items)

    def cancel_order(self, user_id: int, order_id: int) -> OrderResponse:
        """Cancel an order.

        This method ensures atomicity - status update and purchase count
        rollback happen together or not at all.

        Args:
            user_id: ID of the user canceling the order.
            order_id: ID of the order to cancel.

        Returns:
            OrderResponse: Canceled order.

        Raises:
            OrderNotFoundException: If order not found or not owned by user.
            OrderCancelNotAllowedException: If order status is not CREATED.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundException()

        # CREATED 상태에서만 취소 가능
        if order.status != "CREATED":
            raise OrderCancelNotAllowedException()

        with UnitOfWork(self.db) as uow:
            try:
                # 판매량 감소
                for item in order.items:
                    book = self.book_repo.get_by_id(item.book_id)
                    if book:
                        self.book_repo.update_stats(
                            book, purchase_count=max(0, book.purchase_count - item.quantity)
                        )

                # 주문 상태 변경
                order = self.order_repo.update_status(order, "REFUND")

                uow.commit()
                self.db.refresh(order)

            except Exception:
                raise

        return self._build_order_response(order, order.items)

    def get_all_orders(
        self, page: int = 1, size: int = 10, status: Optional[str] = None
    ) -> OrderListResponse:
        """Get all orders with pagination (admin only)."""
        skip = (page - 1) * size
        orders, total = self.order_repo.get_all(skip=skip, limit=size, status=status)

        order_responses = []
        for order in orders:
            order_responses.append(self._build_order_response(order, order.items))

        return OrderListResponse(
            orders=order_responses, total=total, page=page, size=size
        )

    def _build_order_response(self, order, items) -> OrderResponse:
        """Build OrderResponse from order and items."""
        item_responses = []
        for item in items:
            item_responses.append(
                OrderItemResponse(
                    id=item.id,
                    book_id=item.book_id,
                    book_title=item.book.title if item.book else "Unknown",
                    price=item.price,
                    quantity=item.quantity,
                    total_amount=item.total_amount,
                )
            )

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            order_date=order.order_date,
            total_amount=order.total_amount,
            status=order.status,
            items=item_responses,
            created_at=order.created_at,
        )
