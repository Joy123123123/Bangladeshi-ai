"""
Code Assistant API routes.

AI-powered programming help, debugging, and code explanations.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware.rate_limit import ANONYMOUS_LIMIT, limiter
from app.models.ai_models import AIResponse
from app.services import deepseek_service, gemini_service, grok_service
from app.services.bengali_nlp import build_language_instruction, detect_language
from app.utils.prompts import CODE_ASSISTANT_PROMPT
from app.utils.validators import CodeRequest

router = APIRouter()

_MODEL_SERVICES = {
    "gemini": gemini_service,
    "deepseek": deepseek_service,
    "grok": grok_service,
}


@router.post(
    "/help",
    response_model=AIResponse,
    summary="Get AI-powered code help",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(ANONYMOUS_LIMIT)
async def code_help(request: Request, body: CodeRequest):
    """
    Ask a coding question or paste code to get expert help.

    - **question**: Your programming question
    - **code**: *(optional)* Code snippet to debug or explain
    - **programming_language**: e.g. `python`, `javascript`, `java`
    - **model**: AI model to use
    """
    service = _MODEL_SERVICES.get(body.model)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model '{body.model}'.",
        )

    detected_lang = detect_language(body.question)
    lang_instruction = build_language_instruction("auto", detected_lang)

    if body.code:
        prompt = (
            f"Programming language: {body.programming_language}\n\n"
            f"Code:\n```{body.programming_language}\n{body.code}\n```\n\n"
            f"Question: {body.question}"
        )
    else:
        prompt = f"Programming language: {body.programming_language}\n\nQuestion: {body.question}"

    system_prompt = CODE_ASSISTANT_PROMPT + lang_instruction

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
