from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.settlement import Settlement, SettlementOrder


class SettlementRepository:
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

    def create(self, settlement_data: dict) -> Settlement:
        db_settlement = Settlement(**settlement_data)
        self.db.add(db_settlement)
        self.db.commit()
        self.db.refresh(db_settlement)
        return db_settlement

    def add_order(self, settlement_id: int, order_item_id: int) -> SettlementOrder:
        db_order = SettlementOrder(
            settlement_id=settlement_id, order_item_id=order_item_id
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order
