from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.ranking import Ranking


class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_rankings(
        self,
        ranking_type: str,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> List[Ranking]:
        query = (
            self.db.query(Ranking)
            .options(joinedload(Ranking.book))
            .filter(Ranking.ranking_type == ranking_type)
        )

        if age_group:
            query = query.filter(Ranking.age_group == age_group)
        else:
            query = query.filter(Ranking.age_group == "ALL")

        if gender:
            query = query.filter(Ranking.gender == gender)
        else:
            query = query.filter(Ranking.gender == "ALL")

        return query.order_by(Ranking.rank.asc()).limit(limit).all()

    def create(self, ranking_data: dict) -> Ranking:
        db_ranking = Ranking(**ranking_data)
        self.db.add(db_ranking)
        self.db.commit()
        self.db.refresh(db_ranking)
        return db_ranking

    def update(self, ranking: Ranking, update_data: dict) -> Ranking:
        for key, value in update_data.items():
            if value is not None:
                setattr(ranking, key, value)
        self.db.commit()
        self.db.refresh(ranking)
        return ranking

    def delete_all(self) -> None:
        self.db.query(Ranking).delete()
        self.db.commit()
