"""Redis caching layer with graceful fallback."""
import json
import logging
import os
from typing import Any, Optional

from redis import Redis
from redis.exceptions import ConnectionError, RedisError

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis cache manager with graceful fallback to no-cache if Redis is unavailable.
    All methods fail silently if Redis connection fails.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection with fallback.
        
        Args:
            redis_url: Redis connection URL. If not provided, reads from REDIS_URL 
                      environment variable with fallback to redis://localhost:6379
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_url = redis_url
        self.client: Optional[Redis] = None
        self._connect()

    def _connect(self) -> None:
        """Establish Redis connection with error handling."""
        try:
            self.client = Redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info("Redis connection established successfully")
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning(f"Redis connection failed: {e}. Cache operations will be skipped.")
            self.client = None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found or Redis unavailable

        Returns:
            Cached value, parsed JSON if stored as JSON, or default value
        """
        if self.client is None:
            return default

        try:
            value = self.client.get(key)
            if value is None:
                return default

            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as-is if not JSON
                return value
        except RedisError as e:
            logger.warning(f"Cache get failed for key '{key}': {e}")
            return default

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default 5 minutes)

        Returns:
            True if set successfully, False otherwise
        """
        if self.client is None:
            return False

        try:
            # Serialize to JSON for consistent retrieval
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            self.client.setex(key, ttl, serialized_value)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set failed for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if self.client is None:
            return False

        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache delete failed for key '{key}': {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern to match (e.g., "video:*")

        Returns:
            Number of keys deleted
        """
        if self.client is None:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted_count = self.client.delete(*keys)
                logger.info(f"Cleared {deleted_count} cache keys matching pattern '{pattern}'")
                return deleted_count
            return 0
        except RedisError as e:
            logger.warning(f"Cache clear_pattern failed for pattern '{pattern}': {e}")
            return 0

    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self.client is not None


# Singleton instance
cache_manager = CacheManager()

__all__ = ["CacheManager", "cache_manager"]
