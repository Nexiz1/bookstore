from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_ranking_service
from app.schemas.ranking import RankingListResponse, RankingType
from app.schemas.response import SuccessResponse
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get("/", response_model=SuccessResponse[RankingListResponse])
async def get_rankings(
    type: RankingType = Query(RankingType.PURCHASE_COUNT, alias="type"),
    age_group: Optional[str] = Query(None, alias="ageGroup"),
    gender: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    service: RankingService = Depends(get_ranking_service),
):
    """랭킹 조회 (Redis 캐시 우선, Cache Miss 시 DB 조회)

    - type: purchaseCount (판매량 순) 또는 averageRating (평점 순)
    - ageGroup: 연령대 필터링 (선택)
    - gender: 성별 필터링 (선택)
    - limit: 반환할 항목 수 (기본값: 10, 최대: 100)
    """
    result = await service.get_rankings_cached(
        ranking_type=type, age_group=age_group, gender=gender, limit=limit
    )
    return SuccessResponse(data=result)
