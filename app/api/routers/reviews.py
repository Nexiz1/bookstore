from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_review_service
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.schemas.review import ReviewCreate, ReviewListResponse, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()


@router.post(
    "/books/{book_id}/reviews",
    response_model=SuccessResponse[ReviewResponse],
    status_code=201,
)
def create_review(
    book_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    """리뷰 작성 (OrderItems 확인 필수 - 구매자만)"""
    review = service.create_review(current_user.id, book_id, review_data)
    return SuccessResponse(data=review, message="Review created successfully")


@router.get(
    "/books/{book_id}/reviews", response_model=SuccessResponse[ReviewListResponse]
)
def get_book_reviews(
    book_id: int, service: ReviewService = Depends(get_review_service)
):
    """해당 책의 리뷰 목록 조회"""
    result = service.get_book_reviews(book_id)
    return SuccessResponse(data=result)


@router.delete("/reviews/{review_id}", response_model=SuccessResponse)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    """리뷰 삭제 (작성자 또는 Admin)"""
    is_admin = current_user.role == "admin"
    service.delete_review(current_user.id, review_id, is_admin=is_admin)
    return SuccessResponse(message="Review deleted successfully")
