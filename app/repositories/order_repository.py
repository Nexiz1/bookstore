from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.book))
            .filter(Order.id == order_id)
            .first()
        )

    def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> Tuple[List[Order], int]:
        query = self.db.query(Order).filter(Order.user_id == user_id)
        total = query.count()
        orders = (
            query.options(joinedload(Order.items).joinedload(OrderItem.book))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return orders, total

    def get_all(
        self, skip: int = 0, limit: int = 10, status: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        query = self.db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        total = query.count()
        orders = (
            query.options(joinedload(Order.items).joinedload(OrderItem.book))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return orders, total

    def create(self, order_data: dict) -> Order:
        db_order = Order(**order_data)
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def add_item(self, item_data: dict) -> OrderItem:
        db_item = OrderItem(**item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_status(self, order: Order, status: str) -> Order:
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order


class OrderItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[OrderItem]:
        return (
            self.db.query(OrderItem)
            .options(joinedload(OrderItem.book))
            .filter(OrderItem.id == item_id)
            .first()
        )

    def get_by_user_and_book(self, user_id: int, book_id: int) -> Optional[OrderItem]:
        return (
            self.db.query(OrderItem)
            .join(Order)
            .filter(
                Order.user_id == user_id,
                OrderItem.book_id == book_id,
                Order.status != "REFUND",
            )
            .first()
        )

    def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        return self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
