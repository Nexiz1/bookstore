from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RankingType(str, Enum):
    PURCHASE_COUNT = "purchaseCount"
    AVERAGE_RATING = "averageRating"


# ============ Response Schemas ============
class RankingItemResponse(BaseModel):
    """랭킹 아이템 응답"""
    rank: int
    book_id: int
    book_title: str
    book_author: str
    purchase_count: int
    average_rating: Decimal

    class Config:
        from_attributes = True


class RankingListResponse(BaseModel):
    """랭킹 목록 응답"""
    ranking_type: RankingType
    age_group: Optional[str] = None
    gender: Optional[str] = None
    rankings: list[RankingItemResponse]
