from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SaleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ============ Request Schemas ============
class SaleCreate(BaseModel):
    """타임세일 생성 요청"""
    sale_name: str = Field(..., max_length=20)
    discount_rate: Decimal = Field(..., gt=0, le=100)
    started_at: datetime
    ended_at: datetime


class SaleBookAdd(BaseModel):
    """세일 도서 추가 요청"""
    book_id: int


# ============ Response Schemas ============
class SaleResponse(BaseModel):
    """세일 응답"""
    id: int
    sale_name: str
    seller_id: int
    discount_rate: Decimal
    started_at: datetime
    ended_at: datetime
    status: SaleStatus
    created_at: datetime

    class Config:
        from_attributes = True
