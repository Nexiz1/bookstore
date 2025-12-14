"""Ranking repository module for database operations.

This module handles all database CRUD operations for rankings.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.ranking import Ranking


class RankingRepository:
    """Repository for ranking-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

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

    def create(self, ranking_data: dict, *, commit: bool = True) -> Ranking:
        """Create a new ranking.

        Args:
            ranking_data: Dictionary containing ranking fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            Ranking: Created ranking instance.
        """
        db_ranking = Ranking(**ranking_data)
        self.db.add(db_ranking)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_ranking)
        return db_ranking

    def update(self, ranking: Ranking, update_data: dict, *, commit: bool = True) -> Ranking:
        """Update ranking information.

        Args:
            ranking: Ranking instance to update.
            update_data: Dictionary of fields to update.
            commit: If True, commit the transaction. Default True.

        Returns:
            Ranking: Updated ranking instance.
        """
        for key, value in update_data.items():
            if value is not None:
                setattr(ranking, key, value)
        if commit:
            self.db.commit()
            self.db.refresh(ranking)
        return ranking

    def delete_all(self, *, commit: bool = True) -> None:
        """Delete all rankings.

        Args:
            commit: If True, commit the transaction. Default True.
        """
        self.db.query(Ranking).delete()
        if commit:
            self.db.commit()
