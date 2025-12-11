from fastapi import APIRouter, Depends

from app.api.dependencies import get_sale_service, get_seller_user
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.schemas.sale import SaleBookAdd, SaleCreate, SaleResponse
from app.services.sale_service import SaleService

router = APIRouter()


@router.post("/", response_model=SuccessResponse[SaleResponse], status_code=201)
def create_sale(
    sale_data: SaleCreate,
    current_user: User = Depends(get_seller_user),
    service: SaleService = Depends(get_sale_service),
):
    """타임 세일 이벤트 생성 (Seller only)"""
    sale = service.create_sale(current_user.id, sale_data)
    return SuccessResponse(data=sale, message="Sale created successfully")


@router.post("/{sale_id}/books", response_model=SuccessResponse[SaleResponse])
def add_book_to_sale(
    sale_id: int,
    book_data: SaleBookAdd,
    current_user: User = Depends(get_seller_user),
    service: SaleService = Depends(get_sale_service),
):
    """세일 적용 도서 추가 (Seller only)"""
    sale = service.add_book_to_sale(current_user.id, sale_id, book_data)
    return SuccessResponse(data=sale, message="Book added to sale")
