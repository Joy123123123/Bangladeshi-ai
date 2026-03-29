"""
Grammar & Writing Assistant API routes.

Real-time Bengali and English grammar checking and writing improvement.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware.rate_limit import ANONYMOUS_LIMIT, limiter
from app.models.ai_models import AIResponse
from app.services import deepseek_service, gemini_service, grok_service
from app.services.bengali_nlp import build_language_instruction, detect_language, preprocess_bengali_text
from app.utils.prompts import GRAMMAR_SYSTEM_PROMPT
from app.utils.validators import GrammarRequest

router = APIRouter()

_MODEL_SERVICES = {
    "gemini": gemini_service,
    "deepseek": deepseek_service,
    "grok": grok_service,
}


@router.post(
    "/check",
    response_model=AIResponse,
    summary="Check and improve grammar & writing",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(ANONYMOUS_LIMIT)
async def grammar_check(request: Request, body: GrammarRequest):
    """
    Submit text for grammar checking and writing improvement.

    - **text**: The text to check (Bengali or English)
    - **language**: Language hint — `auto`, `bn`, or `en`
    - **model**: AI model to use
    """
    service = _MODEL_SERVICES.get(body.model)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model '{body.model}'.",
        )

    clean_text = preprocess_bengali_text(body.text)
    detected_lang = detect_language(clean_text) if body.language == "auto" else body.language
    lang_instruction = build_language_instruction(body.language, detected_lang)

    prompt = (
        f"Please check the following text for grammar and writing quality:\n\n"
        f"```\n{clean_text}\n```"
    )
    system_prompt = GRAMMAR_SYSTEM_PROMPT + lang_instruction

    try:
        reply = await service.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            history=None,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {exc}",
        ) from exc

    return AIResponse(model=body.model, content=reply)
