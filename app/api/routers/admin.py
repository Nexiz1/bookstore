from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_admin_user, get_order_service, get_settlement_service
from app.models.user import User
from app.schemas.order import OrderListResponse
from app.schemas.response import SuccessResponse
from app.schemas.settlement import SettlementCalculateResponse
from app.services.order_service import OrderService
from app.services.settlement_service import SettlementService

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


@router.post(
    "/settlements/calculate",
    response_model=SuccessResponse[SettlementCalculateResponse],
)
def calculate_settlements(
    admin_user: User = Depends(get_admin_user),
    service: SettlementService = Depends(get_settlement_service),
):
    """정산 데이터 생성 (관리자 트리거)

    ARRIVED 상태의 미정산 주문들을 판매자별로 집계하여
    정산 데이터를 생성합니다.

    - 수수료율: 10%
    - 정산액 = 매출 - 수수료
    """
    result = service.calculate_settlements()
    return SuccessResponse(data=result, message=result.message)
