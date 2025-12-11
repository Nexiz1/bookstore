from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# ============ Response Schemas ============
class SettlementResponse(BaseModel):
    """정산 응답"""
    id: int
    seller_id: int
    total_sales: Decimal
    commission: Decimal
    final_payout: Decimal
    period_start: date
    period_end: date
    settlement_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class SettlementListResponse(BaseModel):
    """정산 목록 응답"""
    settlements: list[SettlementResponse]
    total: int
