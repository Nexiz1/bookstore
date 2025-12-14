"""Ranking service module with Redis caching.

This module provides ranking functionality with Redis caching support.
Rankings are cached in Redis and refreshed every 10 minutes via scheduler.
"""

import json
import logging
from decimal import Decimal
from typing import Optional

import redis.asyncio as redis
from sqlalchemy.orm import Session

from app.core.redis import RANKING_CACHE_TTL, RedisKeys, get_redis_client
from app.repositories.ranking_repository import RankingRepository
from app.schemas.ranking import RankingItemResponse, RankingListResponse, RankingType

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def decimal_decoder(obj: dict) -> dict:
    """Decode Decimal strings back to Decimal objects."""
    if "average_rating" in obj:
        obj["average_rating"] = Decimal(obj["average_rating"])
    return obj


class RankingService:
    """Service class for ranking operations with Redis caching."""

    def __init__(self, db: Session):
        self.db = db
        self.ranking_repo = RankingRepository(db)

    def _get_rankings_from_db(
        self,
        ranking_type: RankingType,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> RankingListResponse:
        """Fetch rankings directly from database.

        Args:
            ranking_type: Type of ranking (PURCHASE_COUNT or AVERAGE_RATING).
            age_group: Age group filter.
            gender: Gender filter.
            limit: Maximum number of results.

        Returns:
            RankingListResponse: Rankings fetched from database.
        """
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

    def get_rankings(
        self,
        ranking_type: RankingType = RankingType.PURCHASE_COUNT,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> RankingListResponse:
        """Get rankings (synchronous version for backward compatibility).

        This method fetches rankings directly from the database.
        For cached rankings, use get_rankings_cached() instead.

        Args:
            ranking_type: Type of ranking.
            age_group: Age group filter.
            gender: Gender filter.
            limit: Maximum number of results.

        Returns:
            RankingListResponse: Rankings data.
        """
        return self._get_rankings_from_db(ranking_type, age_group, gender, limit)

    async def get_rankings_cached(
        self,
        ranking_type: RankingType = RankingType.PURCHASE_COUNT,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> RankingListResponse:
        """Get rankings with Redis caching.

        Attempts to fetch rankings from Redis cache first.
        On cache miss, fetches from database and caches the result.

        Args:
            ranking_type: Type of ranking (PURCHASE_COUNT or AVERAGE_RATING).
            age_group: Age group filter.
            gender: Gender filter.
            limit: Maximum number of results.

        Returns:
            RankingListResponse: Rankings data from cache or database.
        """
        redis_client = await get_redis_client()
        cache_key = RedisKeys.ranking_key(
            ranking_type.value,
            age_group or "ALL",
            gender or "ALL",
        )

        try:
            # Try to get from cache
            cached_data = await redis_client.get(cache_key)

            if cached_data:
                logger.debug(f"Cache HIT for key: {cache_key}")
                data = json.loads(cached_data, object_hook=decimal_decoder)

                # Apply limit to cached data
                rankings_data = data.get("rankings", [])[:limit]

                return RankingListResponse(
                    ranking_type=ranking_type,
                    age_group=age_group,
                    gender=gender,
                    rankings=[RankingItemResponse(**item) for item in rankings_data],
                )

            logger.debug(f"Cache MISS for key: {cache_key}")

        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")

        # Cache miss or error - fetch from database
        result = self._get_rankings_from_db(ranking_type, age_group, gender, limit)

        # Cache the result asynchronously
        try:
            cache_data = json.dumps(result.model_dump(), cls=DecimalEncoder)
            await redis_client.setex(cache_key, RANKING_CACHE_TTL, cache_data)
            logger.debug(f"Cached rankings for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Redis cache write error: {e}")

        return result

    @staticmethod
    async def calculate_and_cache_rankings(db: Session) -> None:
        """Calculate rankings from DB and cache them in Redis.

        This method is called by the scheduler every 10 minutes.
        It calculates rankings for both purchase count and average rating,
        creates Ranking records in DB, and caches them in Redis.

        Args:
            db: Database session.
        """
        logger.info("Starting ranking calculation and caching...")

        from app.models.book import Book

        redis_client = await get_redis_client()
        ranking_repo = RankingRepository(db)

        # 1. 기존 랭킹 데이터 삭제
        ranking_repo.delete_all(commit=True)
        logger.info("Deleted existing rankings")

        ranking_types = [
            (RankingType.PURCHASE_COUNT, "purchaseCount", "purchase_count"),
            (RankingType.AVERAGE_RATING, "averageRating", "average_rating"),
        ]

        for ranking_type, type_value, order_by_column in ranking_types:
            try:
                # 2. Book 테이블에서 상위 10개 조회
                if order_by_column == "purchase_count":
                    top_books = (
                        db.query(Book)
                        .filter(Book.status == "ONSALE")
                        .order_by(Book.purchase_count.desc())
                        .limit(10)
                        .all()
                    )
                else:  # average_rating
                    top_books = (
                        db.query(Book)
                        .filter(Book.status == "ONSALE")
                        .filter(Book.review_count > 0)  # 리뷰가 있는 도서만
                        .order_by(Book.average_rating.desc())
                        .limit(10)
                        .all()
                    )

                # 3. Ranking 테이블에 데이터 삽입
                ranking_items = []
                for idx, book in enumerate(top_books, start=1):
                    ranking_data = {
                        "ranking_type": type_value,
                        "rank": idx,
                        "book_id": book.id,
                        "purchase_count": book.purchase_count,
                        "average_rating": book.average_rating,
                        "age_group": "ALL",
                        "gender": "ALL",
                    }
                    ranking_repo.create(ranking_data, commit=False)

                    ranking_items.append(
                        RankingItemResponse(
                            rank=idx,
                            book_id=book.id,
                            book_title=book.title,
                            book_author=book.author,
                            purchase_count=book.purchase_count,
                            average_rating=book.average_rating,
                        )
                    )

                # 4. DB 커밋
                db.commit()
                logger.info(f"Created {len(ranking_items)} ranking records for {type_value}")

                # 5. Redis 캐싱
                response = RankingListResponse(
                    ranking_type=ranking_type,
                    age_group=None,
                    gender=None,
                    rankings=ranking_items,
                )

                cache_key = RedisKeys.ranking_key(type_value, "ALL", "ALL")
                cache_data = json.dumps(response.model_dump(), cls=DecimalEncoder)
                await redis_client.setex(cache_key, RANKING_CACHE_TTL, cache_data)

                logger.info(f"Cached {len(ranking_items)} items for {type_value} ranking")

            except Exception as e:
                db.rollback()
                logger.error(f"Error calculating {type_value} ranking: {e}")

        logger.info("Ranking calculation and caching completed")
