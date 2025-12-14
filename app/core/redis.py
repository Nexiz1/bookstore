"""Redis client module for caching.

This module provides async Redis client functionality for caching rankings
and other data that benefits from fast, in-memory access.
"""

from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create async Redis client.

    This function creates a singleton Redis client on first call
    and returns the existing instance on subsequent calls.

    Returns:
        redis.Redis: Async Redis client instance.

    Yields:
        redis.Redis: Redis client for dependency injection.
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client connection.

    Should be called during application shutdown to properly
    release Redis connection resources.
    """
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# Redis key constants for rankings
class RedisKeys:
    """Redis key constants for consistent key naming."""

    RANKING_PURCHASE = "ranking:purchase"
    RANKING_RATING = "ranking:rating"

    @staticmethod
    def ranking_key(ranking_type: str, age_group: str = "ALL", gender: str = "ALL") -> str:
        """Generate a ranking cache key.

        Args:
            ranking_type: Type of ranking (purchaseCount or averageRating).
            age_group: Age group filter (default: ALL).
            gender: Gender filter (default: ALL).

        Returns:
            str: Formatted Redis key.
        """
        return f"ranking:{ranking_type}:{age_group}:{gender}"


# Cache TTL constants (in seconds)
RANKING_CACHE_TTL = 720  # 12 minutes (10분 주기 + 2분 여유)
