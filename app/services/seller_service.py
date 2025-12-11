from sqlalchemy.orm import Session

from app.exceptions.seller_exceptions import (
    SellerAlreadyExistsException,
    SellerNotFoundException,
)
from app.repositories.seller_repository import SellerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.seller import SellerCreate, SellerResponse, SellerUpdate


class SellerService:
    def __init__(self, db: Session):
        self.db = db
        self.seller_repo = SellerRepository(db)
        self.user_repo = UserRepository(db)

    def register_seller(
        self, user_id: int, seller_data: SellerCreate
    ) -> SellerResponse:
        # 이미 판매자 프로필이 있는지 확인
        existing_seller = self.seller_repo.get_by_user_id(user_id)
        if existing_seller:
            raise SellerAlreadyExistsException("You already have a seller profile")

        # 사업자명 중복 확인
        if self.seller_repo.get_by_business_name(seller_data.business_name):
            raise SellerAlreadyExistsException("Business name already exists")

        # 이메일 중복 확인
        if self.seller_repo.get_by_email(seller_data.email):
            raise SellerAlreadyExistsException("Seller email already exists")

        # 판매자 프로필 생성
        seller_dict = seller_data.model_dump()
        seller_dict["user_id"] = user_id
        seller = self.seller_repo.create(seller_dict)

        # 사용자 역할 변경
        user = self.user_repo.get_by_id(user_id)
        self.user_repo.update_role(user, "seller")

        return seller

    def get_my_seller_profile(self, user_id: int) -> SellerResponse:
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()
        return seller

    def update_seller_profile(
        self, user_id: int, update_data: SellerUpdate
    ) -> SellerResponse:
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()

        # 사업자명 중복 확인 (변경하려는 경우)
        if update_data.business_name:
            existing = self.seller_repo.get_by_business_name(update_data.business_name)
            if existing and existing.id != seller.id:
                raise SellerAlreadyExistsException("Business name already exists")

        update_dict = update_data.model_dump(exclude_unset=True)
        return self.seller_repo.update(seller, update_dict)
