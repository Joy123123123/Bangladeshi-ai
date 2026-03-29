"""Tests for main.py – FastAPI application entry point."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_returns_200(self):
        """Root endpoint should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_json(self):
        """Root endpoint should return a JSON response."""
        response = client.get("/")
        assert response.headers["content-type"].startswith("application/json")

    def test_root_message_key_present(self):
        """Response JSON must contain a 'message' key."""
        response = client.get("/")
        data = response.json()
        assert "message" in data

    def test_root_message_value(self):
        """'message' value should be the expected welcome string."""
        response = client.get("/")
        data = response.json()
        assert data["message"] == "Welcome to Unlimited Free AI!"

    def test_root_response_has_no_extra_keys(self):
        """Response JSON should contain exactly one key."""
        response = client.get("/")
        data = response.json()
        assert list(data.keys()) == ["message"]


class TestNotFoundRoutes:
    """Tests for routes that do not exist."""

    def test_unknown_path_returns_404(self):
        """GET on a non-existent route should return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_post_to_root_returns_405(self):
        """POST to the root (GET-only) endpoint should return 405 Method Not Allowed."""
        response = client.post("/")
        assert response.status_code == 405

    def test_put_to_root_returns_405(self):
        """PUT to the root (GET-only) endpoint should return 405 Method Not Allowed."""
        response = client.put("/")
        assert response.status_code == 405

    def test_delete_to_root_returns_405(self):
        """DELETE to the root (GET-only) endpoint should return 405 Method Not Allowed."""
        response = client.delete("/")
        assert response.status_code == 405


class TestAppConfiguration:
    """Tests verifying that the FastAPI app is configured correctly."""

    def test_app_is_fastapi_instance(self):
        """The exported `app` object must be a FastAPI application."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_openapi_schema_available(self):
        """OpenAPI schema endpoint should be accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_docs_endpoint_available(self):
        """Swagger UI docs endpoint should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
