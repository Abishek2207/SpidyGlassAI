"""
SpiderGlass AI – Redis async client with Pub/Sub support.
"""
import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.core.config import settings
import logging

logger = logging.getLogger("spiderglass.redis")

_redis_pool: Redis | None = None


async def get_redis() -> Redis:
    """Returns a singleton Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        logger.info("Redis connection pool created.")
    return _redis_pool


async def close_redis() -> None:
    """Close the Redis connection on shutdown."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Redis connection closed.")


async def publish(channel: str, message: str) -> None:
    """Publish a message to a Redis Pub/Sub channel."""
    r = await get_redis()
    await r.publish(channel, message)


async def set_key(key: str, value: str, expire_seconds: int = 3600) -> None:
    """Set a key-value pair in Redis with an expiry."""
    r = await get_redis()
    await r.set(key, value, ex=expire_seconds)


async def get_key(key: str) -> str | None:
    """Get a value from Redis by key."""
    r = await get_redis()
    return await r.get(key)


async def delete_key(key: str) -> None:
    """Delete a key from Redis."""
    r = await get_redis()
    await r.delete(key)
