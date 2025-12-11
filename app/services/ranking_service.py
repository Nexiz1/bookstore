from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.ranking_repository import RankingRepository
from app.schemas.ranking import RankingItemResponse, RankingListResponse, RankingType


class RankingService:
    def __init__(self, db: Session):
        self.db = db
        self.ranking_repo = RankingRepository(db)

    def get_rankings(
        self,
        ranking_type: RankingType = RankingType.PURCHASE_COUNT,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> RankingListResponse:
        rankings = self.ranking_repo.get_rankings(
            ranking_type=ranking_type.value,
            age_group=age_group,
            gender=gender,
            limit=limit,
        )

        ranking_items = []
        for r in rankings:
            ranking_items.append(
                RankingItemResponse(
                    rank=r.rank,
                    book_id=r.book_id,
                    book_title=r.book.title if r.book else "Unknown",
                    book_author=r.book.author if r.book else "Unknown",
                    purchase_count=r.purchase_count,
                    average_rating=r.average_rating,
                )
            )

        return RankingListResponse(
            ranking_type=ranking_type,
            age_group=age_group,
            gender=gender,
            rankings=ranking_items,
        )
