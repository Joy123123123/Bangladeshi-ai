"""Tests for backend/app/services/rag_service.py – ChromaDB RAG service."""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ---------------------------------------------------------------------------
# Mock chromadb before it is imported by rag_service, since the package is
# an optional dependency that may not be installed in the test environment.
# ---------------------------------------------------------------------------

_mock_collection = MagicMock()
_mock_chroma_client = MagicMock()
_mock_chroma_client.create_collection.return_value = _mock_collection

_mock_chromadb = MagicMock()
_mock_chromadb.Client.return_value = _mock_chroma_client

_mock_settings = MagicMock()

sys.modules.setdefault("chromadb", _mock_chromadb)
sys.modules.setdefault("chromadb.config", MagicMock(Settings=_mock_settings))

# Now it is safe to import the module under test.
from backend.app.services.rag_service import RagService  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _fresh_service():
    """Return a new RagService backed by fresh mocks.

    Each call resets the module-level client mock so tests remain independent.
    """
    collection = MagicMock()
    collection.add = MagicMock()
    collection.query = MagicMock(return_value={"ids": [], "documents": []})
    collection.get = MagicMock(return_value={"ids": [], "documents": []})

    client = MagicMock()
    client.create_collection.return_value = collection

    with patch("backend.app.services.rag_service.chroma_client", client):
        service = RagService()

    return service, collection


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRagServiceInit:
    """Tests for RagService.__init__."""

    def test_creates_collection_on_init(self):
        """RagService should create (or get) the 'buet_exam_questions' collection."""
        collection = MagicMock()
        client = MagicMock()
        client.create_collection.return_value = collection

        with patch("backend.app.services.rag_service.chroma_client", client):
            service = RagService()

        client.create_collection.assert_called_once_with("buet_exam_questions")

    def test_collection_attribute_set(self):
        """RagService.collection should reference the collection returned by the client."""
        collection = MagicMock()
        client = MagicMock()
        client.create_collection.return_value = collection

        with patch("backend.app.services.rag_service.chroma_client", client):
            service = RagService()

        assert service.collection is collection


class TestRagServiceAddQuestion:
    """Tests for RagService.add_question."""

    def test_add_question_calls_collection_add(self):
        """add_question should call collection.add with question text and vector."""
        service, collection = _fresh_service()
        service.add_question("What is 2+2?", [0.1, 0.2, 0.3])
        collection.add.assert_called_once_with(["What is 2+2?"], [[0.1, 0.2, 0.3]])

    def test_add_question_passes_text_as_list(self):
        """add_question must wrap the question text in a list."""
        service, collection = _fresh_service()
        service.add_question("Describe recursion.", [1.0, 2.0])
        args, _ = collection.add.call_args
        assert isinstance(args[0], list)
        assert args[0] == ["Describe recursion."]

    def test_add_question_passes_vector_as_list(self):
        """add_question must wrap the vector in a list."""
        service, collection = _fresh_service()
        vector = [0.5, 0.6, 0.7]
        service.add_question("Some question", vector)
        args, _ = collection.add.call_args
        assert isinstance(args[1], list)
        assert args[1] == [vector]

    def test_add_multiple_questions(self):
        """add_question can be called multiple times independently."""
        service, collection = _fresh_service()
        service.add_question("Q1", [1.0])
        service.add_question("Q2", [2.0])
        assert collection.add.call_count == 2

    def test_add_question_returns_none(self):
        """add_question should return None (no explicit return value)."""
        service, collection = _fresh_service()
        collection.add.return_value = None
        result = service.add_question("Test?", [0.0])
        assert result is None

    def test_add_question_with_empty_vector(self):
        """add_question should forward an empty vector without error."""
        service, collection = _fresh_service()
        service.add_question("Empty vector question", [])
        collection.add.assert_called_once_with(["Empty vector question"], [[]])

    def test_add_question_with_empty_text(self):
        """add_question should forward an empty string without error."""
        service, collection = _fresh_service()
        service.add_question("", [0.1])
        collection.add.assert_called_once_with([""], [[0.1]])


class TestRagServiceQuery:
    """Tests for RagService.query."""

    def test_query_calls_collection_query(self):
        """query() should call collection.query with the supplied vector."""
        service, collection = _fresh_service()
        service.query([0.1, 0.2])
        collection.query.assert_called_once()

    def test_query_passes_vector_argument(self):
        """query() must forward the query_vector to collection.query."""
        service, collection = _fresh_service()
        vector = [0.3, 0.4, 0.5]
        service.query(vector)
        args, _ = collection.query.call_args
        assert args[0] == vector

    def test_query_default_n_results_is_5(self):
        """query() should use n_results=5 by default."""
        service, collection = _fresh_service()
        service.query([0.1])
        args, kwargs = collection.query.call_args
        assert 5 in args or kwargs.get("n_results") == 5

    def test_query_custom_n_results(self):
        """query() should forward a custom n_results value."""
        service, collection = _fresh_service()
        service.query([0.1], n_results=10)
        args, kwargs = collection.query.call_args
        assert 10 in args or kwargs.get("n_results") == 10

    def test_query_returns_collection_result(self):
        """query() should return whatever collection.query returns."""
        service, collection = _fresh_service()
        expected = {"ids": ["id1"], "documents": ["doc1"]}
        collection.query.return_value = expected
        result = service.query([0.1, 0.2])
        assert result == expected

    def test_query_returns_empty_result(self):
        """query() should handle and return an empty result set."""
        service, collection = _fresh_service()
        expected = {"ids": [], "documents": []}
        collection.query.return_value = expected
        result = service.query([0.0])
        assert result == expected


class TestRagServiceRetrieveAll:
    """Tests for RagService.retrieve_all_questions."""

    def test_retrieve_all_calls_collection_get(self):
        """retrieve_all_questions() should call collection.get()."""
        service, collection = _fresh_service()
        service.retrieve_all_questions()
        collection.get.assert_called_once()

    def test_retrieve_all_returns_collection_result(self):
        """retrieve_all_questions() should return whatever collection.get returns."""
        service, collection = _fresh_service()
        expected = {"ids": ["q1", "q2"], "documents": ["doc1", "doc2"]}
        collection.get.return_value = expected
        result = service.retrieve_all_questions()
        assert result == expected

    def test_retrieve_all_returns_empty_when_no_questions(self):
        """retrieve_all_questions() should return an empty structure when no data exists."""
        service, collection = _fresh_service()
        expected = {"ids": [], "documents": []}
        collection.get.return_value = expected
        result = service.retrieve_all_questions()
        assert result == expected

