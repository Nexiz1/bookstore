from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_seller_service, get_seller_user
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.schemas.seller import SellerCreate, SellerResponse, SellerUpdate
from app.services.seller_service import SellerService

router = APIRouter()


@router.post("/", response_model=SuccessResponse[SellerResponse], status_code=201)
def register_seller(
    seller_data: SellerCreate,
    current_user: User = Depends(get_current_user),
    service: SellerService = Depends(get_seller_service),
):
    """판매자 등록 신청 (일반 유저 → 판매자)"""
    seller = service.register_seller(current_user.id, seller_data)
    return SuccessResponse(
        data=SellerResponse.model_validate(seller),
        message="Seller registration successful",
    )


@router.get("/me", response_model=SuccessResponse[SellerResponse])
def get_my_seller_profile(
    current_user: User = Depends(get_seller_user),
    service: SellerService = Depends(get_seller_service),
):
    """내 판매자 정보 조회 (매출, 정산계좌 등)"""
    seller = service.get_my_seller_profile(current_user.id)
    return SuccessResponse(data=SellerResponse.model_validate(seller))


@router.patch("/me", response_model=SuccessResponse[SellerResponse])
def update_my_seller_profile(
    update_data: SellerUpdate,
    current_user: User = Depends(get_seller_user),
    service: SellerService = Depends(get_seller_service),
):
    """판매자 정보 수정 (계좌번호, 사업자명 등)"""
    seller = service.update_seller_profile(current_user.id, update_data)
    return SuccessResponse(
        data=SellerResponse.model_validate(seller),
        message="Seller profile updated successfully",
    )
