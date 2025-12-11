from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions.seller_exceptions import SellerNotFoundException
from app.repositories.seller_repository import SellerRepository
from app.repositories.settlement_repository import SettlementRepository
from app.schemas.settlement import SettlementListResponse, SettlementResponse


class SettlementService:
    def __init__(self, db: Session):
        self.db = db
        self.settlement_repo = SettlementRepository(db)
        self.seller_repo = SellerRepository(db)

    def get_my_settlements(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> SettlementListResponse:
        # 판매자 프로필 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()

        settlements, total = self.settlement_repo.get_by_seller_id(
            seller.id, start_date=start_date, end_date=end_date
        )

        return SettlementListResponse(
            settlements=[SettlementResponse.model_validate(s) for s in settlements],
            total=total,
        )
