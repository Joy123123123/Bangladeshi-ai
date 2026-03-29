"""
User Repository

Stores and retrieves user profiles and preferences using MongoDB.
Falls back gracefully if MongoDB is unavailable.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_motor_client():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
        return client
    except ImportError:
        logger.warning("motor package not installed – user profiles disabled.")
        return None


class UserRepository:
    """Async repository for user profiles and preferences."""

    def __init__(self) -> None:
        self._client = None
        self._db = None
        self._collection = None

    def _ensure_db(self):
        if self._client is None:
            self._client = _get_motor_client()
            if self._client is not None:
                self._db = self._client.bangladeshi_ai
                self._collection = self._db.users
        return self._collection

    async def create_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        class_level: Optional[int] = None,
        board: Optional[str] = None,
        preferred_subject: Optional[str] = None,
    ) -> Optional[dict]:
        collection = self._ensure_db()
        if collection is None:
            return None
        try:
            user = {
                "user_id": user_id,
                "name": name,
                "class_level": class_level,
                "board": board,
                "preferred_subject": preferred_subject,
                "data_saver_mode": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await collection.insert_one(user)
            user.pop("_id", None)
            return user
        except Exception as exc:
            logger.warning("Failed to create user %s: %s", user_id, exc)
            return None

    async def get_user(self, user_id: str) -> Optional[dict]:
        collection = self._ensure_db()
        if collection is None:
            return None
        try:
            user = await collection.find_one({"user_id": user_id})
            if user:
                user.pop("_id", None)
            return user
        except Exception as exc:
            logger.warning("Failed to get user %s: %s", user_id, exc)
            return None

    async def update_preferences(
        self,
        user_id: str,
        preferences: dict,
    ) -> bool:
        collection = self._ensure_db()
        if collection is None:
            return False
        try:
            preferences["updated_at"] = datetime.now(timezone.utc)
            result = await collection.update_one(
                {"user_id": user_id},
                {"$set": preferences},
                upsert=True,
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as exc:
            logger.warning("Failed to update preferences for %s: %s", user_id, exc)
            return False


user_repo = UserRepository()
