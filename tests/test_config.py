"""Tests for app/core/config.py – application configuration via Pydantic BaseSettings."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError


class TestConfigFields:
    """Tests that Config correctly reads and validates required fields."""

    def _make_config(self, **env_vars):
        """Helper: build a Config instance with the given environment variables."""
        from app.core.config import Config
        return Config(**env_vars)

    def test_config_loads_all_required_fields(self):
        """Config should load successfully when all required fields are supplied."""
        cfg = self._make_config(
            GEMINI_API_KEY="gemini-key",
            DEEPSEEK_API_KEY="deepseek-key",
            MONGODB_URL="mongodb://localhost:27017",
            REDIS_URL="redis://localhost:6379",
            CHROMADB_URL="http://localhost:8000",
        )
        assert cfg.GEMINI_API_KEY == "gemini-key"
        assert cfg.DEEPSEEK_API_KEY == "deepseek-key"
        assert cfg.MONGODB_URL == "mongodb://localhost:27017"
        assert cfg.REDIS_URL == "redis://localhost:6379"
        assert cfg.CHROMADB_URL == "http://localhost:8000"

    def test_missing_gemini_api_key_raises(self):
        """ValidationError should be raised when GEMINI_API_KEY is missing."""
        with pytest.raises(ValidationError):
            self._make_config(
                DEEPSEEK_API_KEY="deepseek-key",
                MONGODB_URL="mongodb://localhost:27017",
                REDIS_URL="redis://localhost:6379",
                CHROMADB_URL="http://localhost:8000",
            )

    def test_missing_deepseek_api_key_raises(self):
        """ValidationError should be raised when DEEPSEEK_API_KEY is missing."""
        with pytest.raises(ValidationError):
            self._make_config(
                GEMINI_API_KEY="gemini-key",
                MONGODB_URL="mongodb://localhost:27017",
                REDIS_URL="redis://localhost:6379",
                CHROMADB_URL="http://localhost:8000",
            )

    def test_missing_mongodb_url_raises(self):
        """ValidationError should be raised when MONGODB_URL is missing."""
        with pytest.raises(ValidationError):
            self._make_config(
                GEMINI_API_KEY="gemini-key",
                DEEPSEEK_API_KEY="deepseek-key",
                REDIS_URL="redis://localhost:6379",
                CHROMADB_URL="http://localhost:8000",
            )

    def test_missing_redis_url_raises(self):
        """ValidationError should be raised when REDIS_URL is missing."""
        with pytest.raises(ValidationError):
            self._make_config(
                GEMINI_API_KEY="gemini-key",
                DEEPSEEK_API_KEY="deepseek-key",
                MONGODB_URL="mongodb://localhost:27017",
                CHROMADB_URL="http://localhost:8000",
            )

    def test_missing_chromadb_url_raises(self):
        """ValidationError should be raised when CHROMADB_URL is missing."""
        with pytest.raises(ValidationError):
            self._make_config(
                GEMINI_API_KEY="gemini-key",
                DEEPSEEK_API_KEY="deepseek-key",
                MONGODB_URL="mongodb://localhost:27017",
                REDIS_URL="redis://localhost:6379",
            )

    def test_all_fields_missing_raises(self):
        """ValidationError should be raised when no fields are provided."""
        with pytest.raises(ValidationError):
            self._make_config()

    def test_config_fields_are_strings(self):
        """All configuration values must be stored as strings."""
        cfg = self._make_config(
            GEMINI_API_KEY="g-key",
            DEEPSEEK_API_KEY="d-key",
            MONGODB_URL="mongodb://localhost:27017",
            REDIS_URL="redis://localhost:6379",
            CHROMADB_URL="http://localhost:8000",
        )
        assert isinstance(cfg.GEMINI_API_KEY, str)
        assert isinstance(cfg.DEEPSEEK_API_KEY, str)
        assert isinstance(cfg.MONGODB_URL, str)
        assert isinstance(cfg.REDIS_URL, str)
        assert isinstance(cfg.CHROMADB_URL, str)

    def test_config_field_values_are_preserved_exactly(self):
        """Config must store field values without modification."""
        url = "mongodb+srv://user:p%40ss@cluster0.example.net/db?retryWrites=true"
        cfg = self._make_config(
            GEMINI_API_KEY="key1",
            DEEPSEEK_API_KEY="key2",
            MONGODB_URL=url,
            REDIS_URL="redis://localhost:6379",
            CHROMADB_URL="http://localhost:8000",
        )
        assert cfg.MONGODB_URL == url

    def test_config_env_file_setting(self):
        """Config model_config should specify the expected .env file."""
        from app.core.config import Config
        assert Config.model_config.get("env_file") == ".env"
        assert Config.model_config.get("env_file_encoding") == "utf-8"

    def test_config_from_environment_variables(self, monkeypatch):
        """Config should read values from environment variables."""
        monkeypatch.setenv("GEMINI_API_KEY", "env-gemini")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "env-deepseek")
        monkeypatch.setenv("MONGODB_URL", "mongodb://envhost:27017")
        monkeypatch.setenv("REDIS_URL", "redis://envhost:6379")
        monkeypatch.setenv("CHROMADB_URL", "http://envhost:8000")

        from app.core.config import Config
        cfg = Config()
        assert cfg.GEMINI_API_KEY == "env-gemini"
        assert cfg.DEEPSEEK_API_KEY == "env-deepseek"
        assert cfg.MONGODB_URL == "mongodb://envhost:27017"
        assert cfg.REDIS_URL == "redis://envhost:6379"
        assert cfg.CHROMADB_URL == "http://envhost:8000"
