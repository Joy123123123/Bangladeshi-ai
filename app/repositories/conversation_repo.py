"""
Conversation Repository

Stores and retrieves chat history using MongoDB (Motor async driver).
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
        logger.warning("motor package not installed – conversation history disabled.")
        return None


class ConversationRepository:
    """Async repository for chat conversations."""

    def __init__(self) -> None:
        self._client = None
        self._db = None
        self._collection = None

    def _ensure_db(self):
        if self._client is None:
            self._client = _get_motor_client()
            if self._client is not None:
                self._db = self._client.bangladeshi_ai
                self._collection = self._db.conversations
        return self._collection

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        subject: Optional[str] = None,
        class_level: Optional[int] = None,
        model_used: Optional[str] = None,
    ) -> bool:
        collection = self._ensure_db()
        if collection is None:
            return False
        try:
            await collection.insert_one({
                "session_id": session_id,
                "role": role,
                "content": content,
                "subject": subject,
                "class_level": class_level,
                "model_used": model_used,
                "created_at": datetime.now(timezone.utc),
            })
            return True
        except Exception as exc:
            logger.warning("Failed to save message: %s", exc)
            return False

    async def get_history(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[dict]:
        collection = self._ensure_db()
        if collection is None:
            return []
        try:
            cursor = collection.find(
                {"session_id": session_id},
                sort=[("created_at", 1)],
            ).limit(limit)
            messages = await cursor.to_list(length=limit)
            for msg in messages:
                msg.pop("_id", None)
            return messages
        except Exception as exc:
            logger.warning("Failed to get conversation history: %s", exc)
            return []

    async def delete_session(self, session_id: str) -> bool:
        collection = self._ensure_db()
        if collection is None:
            return False
        try:
            await collection.delete_many({"session_id": session_id})
            return True
        except Exception as exc:
            logger.warning("Failed to delete session %s: %s", session_id, exc)
            return False


conversation_repo = ConversationRepository()
