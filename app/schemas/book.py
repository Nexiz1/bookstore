from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BookStatus(str, Enum):
    SOLDOUT = "SOLDOUT"
    ONSALE = "ONSALE"
    TOBESOLD = "TOBESOLD"


class BookSortBy(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    RATING = "rating"
    SALES = "sales"


# ============ Request Schemas ============
class BookCreate(BaseModel):
    """도서 등록 요청"""
    title: str = Field(..., max_length=20)
    author: str = Field(..., max_length=20)
    publisher: str = Field(..., max_length=20)
    summary: str = Field(..., max_length=100)
    isbn: str = Field(..., max_length=15)
    price: Decimal = Field(..., gt=0)
    publication_date: Optional[date] = None
    status: BookStatus = BookStatus.TOBESOLD


class BookUpdate(BaseModel):
    """도서 수정 요청"""
    title: Optional[str] = Field(None, max_length=20)
    author: Optional[str] = Field(None, max_length=20)
    publisher: Optional[str] = Field(None, max_length=20)
    summary: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)
    publication_date: Optional[date] = None
    status: Optional[BookStatus] = None


# ============ Response Schemas ============
class BookResponse(BaseModel):
    """도서 상세 응답"""
    id: int
    seller_id: int
    title: str
    author: str
    publisher: str
    summary: str
    isbn: str
    price: Decimal
    status: BookStatus
    average_rating: Decimal
    review_count: int
    purchase_count: int
    publication_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """도서 목록 응답"""
    books: list[BookResponse]
    total: int
    page: int
    size: int
