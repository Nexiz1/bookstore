from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_seller_user, get_settlement_service
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.schemas.settlement import SettlementListResponse
from app.services.settlement_service import SettlementService

router = APIRouter()


@router.get("/", response_model=SuccessResponse[SettlementListResponse])
def get_my_settlements(
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    current_user: User = Depends(get_seller_user),
    service: SettlementService = Depends(get_settlement_service),
):
    """정산 내역 조회 (기간별) - Seller only"""
    result = service.get_my_settlements(
        current_user.id, start_date=start_date, end_date=end_date
    )
    return SuccessResponse(data=result)
