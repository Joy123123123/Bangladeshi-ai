"""
Chat API routes.

Provides a unified multi-model chat interface supporting
Gemini, DeepSeek, and Grok.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.middleware.rate_limit import ANONYMOUS_LIMIT, limiter
from app.models.ai_models import AIResponse, SupportedModels
from app.services import deepseek_service, gemini_service, grok_service
from app.services.bengali_nlp import build_language_instruction, detect_language, preprocess_bengali_text
from app.utils.prompts import CHAT_SYSTEM_PROMPT
from app.utils.validators import ChatRequest

router = APIRouter()

_MODEL_SERVICES = {
    "gemini": gemini_service,
    "deepseek": deepseek_service,
    "grok": grok_service,
}


@router.get("/models", response_model=SupportedModels, summary="List available AI models")
async def list_models():
    """Return the list of AI models available on this platform."""
    return SupportedModels(
        models=list(_MODEL_SERVICES.keys()),
        default="gemini",
    )


@router.post(
    "/",
    response_model=AIResponse,
    summary="Send a message and receive an AI response",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(ANONYMOUS_LIMIT)
async def chat(request: Request, body: ChatRequest):
    """
    Send a message to the selected AI model and receive a response.

    - **message**: Your text message (Bengali or English)
    - **model**: `gemini` (default), `deepseek`, or `grok`
    - **conversation_id**: Supply to continue an existing conversation
    - **language**: `auto` (default), `bn` (Bengali), or `en` (English)
    """
    service = _MODEL_SERVICES.get(body.model)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model '{body.model}'. Choose from: {list(_MODEL_SERVICES)}",
        )

    # Pre-process text and detect language
    clean_message = preprocess_bengali_text(body.message)
    detected_lang = detect_language(clean_message)
    lang_instruction = build_language_instruction(body.language, detected_lang)

    system_prompt = CHAT_SYSTEM_PROMPT + lang_instruction

    try:
        reply = await service.generate_response(
            prompt=clean_message,
            system_prompt=system_prompt,
            history=None,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {exc}",
        ) from exc

    conversation_id = body.conversation_id or str(uuid.uuid4())

    return AIResponse(
        model=body.model,
        content=reply,
        conversation_id=conversation_id,
    )
