from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_book_service, get_seller_user
from app.models.user import User
from app.schemas.book import (
    BookCreate,
    BookListResponse,
    BookResponse,
    BookSortBy,
    BookUpdate,
)
from app.schemas.response import SuccessResponse
from app.services.book_service import BookService

router = APIRouter()


@router.post("/", response_model=SuccessResponse[BookResponse], status_code=201)
def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_seller_user),
    service: BookService = Depends(get_book_service),
):
    """도서 등록 (Seller only)"""
    book = service.create_book(current_user.id, book_data)
    return SuccessResponse(
        data=BookResponse.model_validate(book), message="Book created successfully"
    )


@router.get("/", response_model=SuccessResponse[BookListResponse])
def get_books(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    sort: BookSortBy = BookSortBy.DATE_DESC,
    service: BookService = Depends(get_book_service),
):
    """도서 목록 조회 (검색, 정렬, 필터)"""
    result = service.get_books(
        page=page, size=size, keyword=keyword, category=category, sort=sort
    )
    return SuccessResponse(data=result)


@router.get("/{book_id}", response_model=SuccessResponse[BookResponse])
def get_book(book_id: int, service: BookService = Depends(get_book_service)):
    """도서 상세 조회"""
    book = service.get_book(book_id)
    return SuccessResponse(data=BookResponse.model_validate(book))


@router.patch("/{book_id}", response_model=SuccessResponse[BookResponse])
def update_book(
    book_id: int,
    update_data: BookUpdate,
    current_user: User = Depends(get_seller_user),
    service: BookService = Depends(get_book_service),
):
    """도서 정보 수정 (Seller - 본인 책만)"""
    book = service.update_book(current_user.id, book_id, update_data)
    return SuccessResponse(
        data=BookResponse.model_validate(book), message="Book updated successfully"
    )


@router.delete("/{book_id}", response_model=SuccessResponse)
def delete_book(
    book_id: int,
    current_user: User = Depends(get_seller_user),
    service: BookService = Depends(get_book_service),
):
    """도서 삭제 (상태 변경: SOLDOUT) (Seller - 본인 책만)"""
    service.delete_book(current_user.id, book_id)
    return SuccessResponse(message="Book deleted successfully")
