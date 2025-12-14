from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============ Request Schemas ============
class ReviewCreate(BaseModel):
    """리뷰 작성 요청"""
    order_item_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewUpdate(BaseModel):
    """리뷰 수정 요청"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


# ============ Response Schemas ============
class ReviewResponse(BaseModel):
    """리뷰 응답"""
    id: int
    user_id: int
    user_name: str
    book_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """리뷰 목록 응답"""
    reviews: list[ReviewResponse]
    total: int
    average_rating: float
