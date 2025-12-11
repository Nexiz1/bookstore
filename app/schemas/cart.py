from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ============ Request Schemas ============
class CartCreate(BaseModel):
    """장바구니 추가 요청"""
    book_id: int
    quantity: int = Field(default=1, ge=1)


class CartUpdate(BaseModel):
    """장바구니 수량 변경"""
    quantity: int = Field(..., ge=1)


# ============ Response Schemas ============
class CartItemResponse(BaseModel):
    """장바구니 아이템 응답"""
    id: int
    book_id: int
    book_title: str
    book_price: Decimal
    quantity: int
    subtotal: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class CartListResponse(BaseModel):
    """장바구니 목록 응답"""
    items: list[CartItemResponse]
    total_amount: Decimal
    total_items: int
