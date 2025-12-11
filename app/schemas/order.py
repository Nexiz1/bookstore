from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    SHIPPED = "SHIPPED"
    ARRIVED = "ARRIVED"
    REFUND = "REFUND"


# ============ Request Schemas ============
class OrderCreate(BaseModel):
    """주문 생성 요청 (장바구니 아이템들로 주문)"""
    cart_item_ids: Optional[list[int]] = None  # None이면 전체 장바구니


# ============ Response Schemas ============
class OrderItemResponse(BaseModel):
    """주문 상품 응답"""
    id: int
    book_id: int
    book_title: str
    price: Decimal
    quantity: int
    total_amount: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """주문 응답"""
    id: int
    user_id: int
    order_date: datetime
    total_amount: Decimal
    status: OrderStatus
    items: list[OrderItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """주문 목록 응답"""
    orders: list[OrderResponse]
    total: int
    page: int
    size: int
