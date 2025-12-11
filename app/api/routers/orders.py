from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_admin_user, get_current_user, get_order_service
from app.models.user import User
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse
from app.schemas.response import SuccessResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/", response_model=SuccessResponse[OrderResponse], status_code=201)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """주문 생성 (장바구니 결제)"""
    order = service.create_order(current_user.id, order_data)
    return SuccessResponse(data=order, message="Order created successfully")


@router.get("/", response_model=SuccessResponse[OrderListResponse])
def get_my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """내 주문 내역 조회 (페이지네이션)"""
    result = service.get_my_orders(current_user.id, page=page, size=size)
    return SuccessResponse(data=result)


@router.get("/{order_id}", response_model=SuccessResponse[OrderResponse])
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """주문 상세 조회 (주문 상품 포함)"""
    order = service.get_order(current_user.id, order_id)
    return SuccessResponse(data=order)


@router.post("/{order_id}/cancel", response_model=SuccessResponse[OrderResponse])
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    """주문 취소"""
    order = service.cancel_order(current_user.id, order_id)
    return SuccessResponse(data=order, message="Order cancelled successfully")
