"""
Pydantic response/request schemas for AI model interactions.
"""

from typing import List, Optional

from pydantic import BaseModel


class AIMessage(BaseModel):
    role: str          # "user" | "assistant"
    content: str


class AIResponse(BaseModel):
    """Standardised response returned by every AI service."""

    model: str
    content: str
    conversation_id: Optional[str] = None
    tokens_used: Optional[int] = None
    history: Optional[List[AIMessage]] = None


class SupportedModels(BaseModel):
    models: List[str]
    default: str
