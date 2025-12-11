from fastapi import APIRouter, Depends

from app.api.dependencies import get_cart_service, get_current_user
from app.models.user import User
from app.schemas.cart import CartCreate, CartItemResponse, CartListResponse, CartUpdate
from app.schemas.response import SuccessResponse
from app.services.cart_service import CartService

router = APIRouter()


@router.get("/", response_model=SuccessResponse[CartListResponse])
def get_my_cart(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    """내 장바구니 목록 조회"""
    result = service.get_my_cart(current_user.id)
    return SuccessResponse(data=result)


@router.post("/", response_model=SuccessResponse[CartItemResponse], status_code=201)
def add_to_cart(
    cart_data: CartCreate,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    """장바구니 담기"""
    item = service.add_to_cart(current_user.id, cart_data)
    return SuccessResponse(data=item, message="Item added to cart")


@router.patch("/{cart_id}", response_model=SuccessResponse[CartItemResponse])
def update_cart_quantity(
    cart_id: int,
    update_data: CartUpdate,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    """수량 변경"""
    item = service.update_quantity(current_user.id, cart_id, update_data)
    return SuccessResponse(data=item, message="Quantity updated")


@router.delete("/{cart_id}", response_model=SuccessResponse)
def remove_from_cart(
    cart_id: int,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    """장바구니 아이템 삭제"""
    service.remove_from_cart(current_user.id, cart_id)
    return SuccessResponse(message="Item removed from cart")
