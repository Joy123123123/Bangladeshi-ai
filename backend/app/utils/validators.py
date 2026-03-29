"""
Input validators for request payloads.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MessageValidator(BaseModel):
    """Validates a single chat message."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=32_000)


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(..., min_length=1, max_length=8000, description="User message")
    model: str = Field(default="gemini", description="AI model to use: gemini | deepseek | grok")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID")
    language: str = Field(default="auto", description="Response language: auto | bn | en")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        allowed = {"gemini", "deepseek", "grok"}
        if v not in allowed:
            raise ValueError(f"Model must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {"auto", "bn", "en"}
        if v not in allowed:
            raise ValueError(f"Language must be one of: {', '.join(sorted(allowed))}")
        return v


class StudyRequest(BaseModel):
    """Request body for the study helper endpoint."""

    question: str = Field(..., min_length=1, max_length=8000)
    subject: str = Field(
        default="general",
        description="Subject: math | science | history | literature | general",
    )
    model: str = Field(default="gemini")

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        allowed = {"math", "science", "history", "literature", "general"}
        if v not in allowed:
            raise ValueError(f"Subject must be one of: {', '.join(sorted(allowed))}")
        return v


class GrammarRequest(BaseModel):
    """Request body for the grammar checker endpoint."""

    text: str = Field(..., min_length=1, max_length=8000)
    language: str = Field(default="auto", description="Text language: auto | bn | en")
    model: str = Field(default="gemini")


class CodeRequest(BaseModel):
    """Request body for the code assistant endpoint."""

    code: Optional[str] = Field(default=None, max_length=16_000)
    question: str = Field(..., min_length=1, max_length=4000)
    programming_language: str = Field(default="python")
    model: str = Field(default="gemini")


class UserCreateRequest(BaseModel):
    """Request body for user registration."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserLoginRequest(BaseModel):
    """Request body for user login."""

    username: str
    password: str
