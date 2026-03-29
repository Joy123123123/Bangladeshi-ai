"""
Cache Service

Redis-backed caching for NCTB FAQs and AI responses.
Falls back gracefully if Redis is unavailable.
"""

import hashlib
import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_redis_client():
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        return client
    except ImportError:
        logger.warning("redis package not installed – caching disabled.")
        return None
    except Exception as exc:
        logger.error("Failed to connect to Redis: %s", exc)
        return None


class CacheService:
    """Simple Redis cache with automatic fallback to no-op mode."""

    def __init__(self) -> None:
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            self._client = _get_redis_client()
        return self._client

    @staticmethod
    def build_key(prefix: str, *parts: str) -> str:
        raw = ":".join(str(p) for p in parts)
        digest = hashlib.md5(raw.encode()).hexdigest()[:12]
        return f"{prefix}:{digest}"

    async def get(self, key: str) -> Optional[str]:
        client = self._ensure_client()
        if client is None:
            return None
        try:
            value = await client.get(key)
            if value:
                logger.debug("Cache HIT: %s", key)
            return value
        except Exception as exc:
            logger.warning("Cache GET error for %s: %s", key, exc)
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        client = self._ensure_client()
        if client is None:
            return False
        try:
            await client.set(key, value, ex=ttl)
            logger.debug("Cache SET: %s (TTL=%ds)", key, ttl)
            return True
        except Exception as exc:
            logger.warning("Cache SET error for %s: %s", key, exc)
            return False

    async def delete(self, key: str) -> bool:
        client = self._ensure_client()
        if client is None:
            return False
        try:
            await client.delete(key)
            return True
        except Exception as exc:
            logger.warning("Cache DELETE error for %s: %s", key, exc)
            return False

    async def get_json(self, key: str) -> Optional[dict]:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set_json(self, key: str, value: dict, ttl: int = 3600) -> bool:
        return await self.set(key, json.dumps(value, ensure_ascii=False), ttl=ttl)

    async def increment(self, key: str, ttl: int = 60) -> int:
        """Increment a counter (used by rate limiter)."""
        client = self._ensure_client()
        if client is None:
            return 0
        try:
            pipe = client.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, ttl)
            results = await pipe.execute()
            return results[0]
        except Exception as exc:
            logger.warning("Cache INCREMENT error for %s: %s", key, exc)
            return 0


cache_service = CacheService()
