from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_ranking_service
from app.schemas.ranking import RankingListResponse, RankingType
from app.schemas.response import SuccessResponse
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get("/", response_model=SuccessResponse[RankingListResponse])
def get_rankings(
    type: RankingType = Query(RankingType.PURCHASE_COUNT, alias="type"),
    age_group: Optional[str] = Query(None, alias="ageGroup"),
    gender: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    service: RankingService = Depends(get_ranking_service),
):
    """랭킹 조회 (type: purchase/rating, ageGroup, gender)"""
    result = service.get_rankings(
        ranking_type=type, age_group=age_group, gender=gender, limit=limit
    )
    return SuccessResponse(data=result)
