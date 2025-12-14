"""Settlement repository module for database operations.

This module handles all database CRUD operations for settlements.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.settlement import Settlement, SettlementOrder


class SettlementRepository:
    """Repository for settlement-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, settlement_id: int) -> Optional[Settlement]:
        return self.db.query(Settlement).filter(Settlement.id == settlement_id).first()

    def get_by_seller_id(
        self,
        seller_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Settlement], int]:
        query = self.db.query(Settlement).filter(Settlement.seller_id == seller_id)

        if start_date:
            query = query.filter(Settlement.period_start >= start_date)
        if end_date:
            query = query.filter(Settlement.period_end <= end_date)

        total = query.count()
        settlements = query.order_by(Settlement.settlement_date.desc()).all()
        return settlements, total

    def create(self, settlement_data: dict, *, commit: bool = True) -> Settlement:
        """Create a new settlement.

        Args:
            settlement_data: Dictionary containing settlement fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            Settlement: Created settlement instance.
        """
        db_settlement = Settlement(**settlement_data)
        self.db.add(db_settlement)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_settlement)
        return db_settlement

    def add_order(self, settlement_id: int, order_item_id: int, *, commit: bool = True) -> SettlementOrder:
        """Add an order to a settlement.

        Args:
            settlement_id: ID of the settlement.
            order_item_id: ID of the order item to add.
            commit: If True, commit the transaction. Default True.

        Returns:
            SettlementOrder: Created settlement order instance.
        """
        db_order = SettlementOrder(
            settlement_id=settlement_id, order_item_id=order_item_id
        )
        self.db.add(db_order)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_order)
        return db_order

    def get_unsettled_order_items(self) -> List[OrderItem]:
        """Get order items that are ARRIVED but not yet settled.

        Returns:
            List[OrderItem]: List of unsettled order items with book info loaded.
        """
        # Subquery to get order_item_ids that are already settled
        settled_item_ids = (
            self.db.query(SettlementOrder.order_item_id)
            .subquery()
        )

        # Get ARRIVED order items that are not in settlement_order
        return (
            self.db.query(OrderItem)
            .join(Order)
            .options(joinedload(OrderItem.book))
            .filter(
                Order.status == "ARRIVED",
                ~OrderItem.id.in_(settled_item_ids),
            )
            .all()
        )

    def is_order_item_settled(self, order_item_id: int) -> bool:
        """Check if an order item has already been settled.

        Args:
            order_item_id: ID of the order item to check.

        Returns:
            bool: True if already settled, False otherwise.
        """
        return (
            self.db.query(SettlementOrder)
            .filter(SettlementOrder.order_item_id == order_item_id)
            .first()
            is not None
        )
