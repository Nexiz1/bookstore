from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_favorite_service
from app.models.user import User
from app.schemas.favorite import FavoriteBookResponse, FavoriteListResponse
from app.schemas.response import SuccessResponse
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.post(
    "/books/{book_id}/favorites",
    response_model=SuccessResponse[FavoriteBookResponse],
    status_code=201,
)
def add_favorite(
    book_id: int,
    current_user: User = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
):
    """찜하기 등록"""
    favorite = service.add_favorite(current_user.id, book_id)
    return SuccessResponse(data=favorite, message="Added to favorites")


@router.delete("/books/{book_id}/favorites", response_model=SuccessResponse)
def remove_favorite(
    book_id: int,
    current_user: User = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
):
    """찜하기 취소"""
    service.remove_favorite(current_user.id, book_id)
    return SuccessResponse(message="Removed from favorites")


@router.get("/favorites", response_model=SuccessResponse[FavoriteListResponse])
def get_my_favorites(
    current_user: User = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
):
    """내가 찜한 목록 조회"""
    result = service.get_my_favorites(current_user.id)
    return SuccessResponse(data=result)
