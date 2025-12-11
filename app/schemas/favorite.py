from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# ============ Response Schemas ============
class FavoriteBookResponse(BaseModel):
    """찜한 도서 응답"""
    id: int
    book_id: int
    book_title: str
    book_author: str
    book_price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """찜 목록 응답"""
    favorites: list[FavoriteBookResponse]
    total: int
