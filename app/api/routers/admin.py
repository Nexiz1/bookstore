from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_admin_user, get_order_service
from app.models.user import User
from app.schemas.order import OrderListResponse
from app.schemas.response import SuccessResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.get("/orders", response_model=SuccessResponse[OrderListResponse])
def get_all_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    service: OrderService = Depends(get_order_service),
):
    """전체 주문 현황 조회 (관리자용)"""
    result = service.get_all_orders(page=page, size=size, status=status)
    return SuccessResponse(data=result)
