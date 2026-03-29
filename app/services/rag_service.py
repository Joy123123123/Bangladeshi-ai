"""
RAG (Retrieval-Augmented Generation) Service

Uses ChromaDB as a local vector store to retrieve:
  - Previous year exam questions (BUET, DU, Medical, BCS, SSC, HSC)
  - Subject-specific shortcuts and study tips
"""

import logging
from typing import Optional

from app.core.config import settings
from app.core.prompts_bn import RAG_CONTEXT_TEMPLATE

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lazy ChromaDB import so the app still starts if ChromaDB is not installed
# ---------------------------------------------------------------------------

def _get_chroma_client():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
        return client
    except ImportError:
        logger.warning("ChromaDB not installed – RAG features disabled.")
        return None
    except Exception as exc:
        logger.error("Failed to initialise ChromaDB: %s", exc)
        return None


# ---------------------------------------------------------------------------
# RAG Service
# ---------------------------------------------------------------------------

class RAGService:
    """Query ChromaDB for previous-year questions and study shortcuts."""

    def __init__(self) -> None:
        self._client = None
        self._questions_collection = None
        self._shortcuts_collection = None

    def _ensure_client(self) -> bool:
        """Lazily initialise the ChromaDB client and collections."""
        if self._client is not None:
            return True
        self._client = _get_chroma_client()
        if self._client is None:
            return False
        try:
            self._questions_collection = self._client.get_or_create_collection(
                name=settings.RAG_COLLECTION_QUESTIONS,
                metadata={"hnsw:space": "cosine"},
            )
            self._shortcuts_collection = self._client.get_or_create_collection(
                name=settings.RAG_COLLECTION_SHORTCUTS,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ChromaDB collections initialised successfully.")
            return True
        except Exception as exc:
            logger.error("ChromaDB collection init failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Public query methods
    # ------------------------------------------------------------------

    async def query(
        self,
        query: str,
        subject: Optional[str] = None,
        class_level: Optional[int] = None,
        exam_type: Optional[str] = None,
        top_k: int | None = None,
    ) -> str:
        """
        Query the question bank and shortcut store.

        Returns a formatted context string ready to be injected into the
        LLM system prompt.
        """
        if not self._ensure_client():
            return ""

        top_k = top_k or settings.RAG_TOP_K
        contexts: list[str] = []

        questions_ctx = await self._query_questions(
            query=query,
            subject=subject,
            class_level=class_level,
            exam_type=exam_type,
            top_k=top_k,
        )
        if questions_ctx:
            contexts.append(questions_ctx)

        shortcuts_ctx = await self._query_shortcuts(
            query=query,
            subject=subject,
            top_k=max(2, top_k // 2),
        )
        if shortcuts_ctx:
            contexts.append(shortcuts_ctx)

        if not contexts:
            return ""

        combined = "\n\n".join(contexts)
        return RAG_CONTEXT_TEMPLATE.format(context=combined)

    async def _query_questions(
        self,
        query: str,
        subject: Optional[str],
        class_level: Optional[int],
        exam_type: Optional[str],
        top_k: int,
    ) -> str:
        """Retrieve previous-year questions from ChromaDB."""
        if self._questions_collection is None:
            return ""
        try:
            where: dict = {}
            if subject:
                where["subject"] = subject
            if class_level:
                where["class_level"] = class_level
            if exam_type and exam_type != "General":
                where["exam_type"] = exam_type

            query_kwargs: dict = {
                "query_texts": [query],
                "n_results": top_k,
            }
            if where:
                query_kwargs["where"] = where

            results = self._questions_collection.query(**query_kwargs)
            return self._format_results(results, "পূর্ববর্তী বছরের প্রশ্ন")
        except Exception as exc:
            logger.warning("Question query failed: %s", exc)
            return ""

    async def _query_shortcuts(
        self,
        query: str,
        subject: Optional[str],
        top_k: int,
    ) -> str:
        """Retrieve study shortcuts and tips from ChromaDB."""
        if self._shortcuts_collection is None:
            return ""
        try:
            query_kwargs: dict = {
                "query_texts": [query],
                "n_results": top_k,
            }
            if subject:
                query_kwargs["where"] = {"subject": subject}

            results = self._shortcuts_collection.query(**query_kwargs)
            return self._format_results(results, "শর্টকাট ও কৌশল")
        except Exception as exc:
            logger.warning("Shortcuts query failed: %s", exc)
            return ""

    # ------------------------------------------------------------------
    # Data ingestion helpers (call these to populate the vector store)
    # ------------------------------------------------------------------

    async def add_questions(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> bool:
        """Add questions to the ChromaDB question bank."""
        if not self._ensure_client() or self._questions_collection is None:
            return False
        try:
            self._questions_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Added %d questions to ChromaDB.", len(documents))
            return True
        except Exception as exc:
            logger.error("Failed to add questions: %s", exc)
            return False

    async def add_shortcuts(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> bool:
        """Add shortcuts/tips to the ChromaDB shortcut store."""
        if not self._ensure_client() or self._shortcuts_collection is None:
            return False
        try:
            self._shortcuts_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Added %d shortcuts to ChromaDB.", len(documents))
            return True
        except Exception as exc:
            logger.error("Failed to add shortcuts: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_results(results: dict, section_title: str) -> str:
        """Format ChromaDB query results as a readable Bengali string."""
        docs: list[list[str]] = results.get("documents", [[]])
        distances: list[list[float]] = results.get("distances", [[]])
        metadatas: list[list[dict]] = results.get("metadatas", [[]])

        if not docs or not docs[0]:
            return ""

        lines: list[str] = [f"### {section_title}"]
        for i, (doc, meta) in enumerate(zip(docs[0], metadatas[0] if metadatas else [{}] * len(docs[0]))):
            distance = distances[0][i] if distances and distances[0] else None
            relevance = f" (প্রাসঙ্গিকতা: {1 - distance:.0%})" if distance is not None else ""
            source = meta.get("source", "")
            year = meta.get("year", "")
            prefix_parts = [p for p in [source, year] if p]
            prefix = f"[{', '.join(prefix_parts)}]" if prefix_parts else ""
            lines.append(f"{i + 1}. {prefix}{relevance}\n   {doc}")

        return "\n".join(lines)


rag_service = RAGService()
