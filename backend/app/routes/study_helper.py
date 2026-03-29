"""
Study Helper API routes.

Subject-specific AI tutoring for Bengali students.
Supported subjects: Math, Science, History, Literature, General.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware.rate_limit import ANONYMOUS_LIMIT, limiter
from app.models.ai_models import AIResponse
from app.services import deepseek_service, gemini_service, grok_service
from app.services.bengali_nlp import build_language_instruction, detect_language, preprocess_bengali_text
from app.utils.prompts import STUDY_HELPER_PROMPT
from app.utils.validators import StudyRequest

router = APIRouter()

_MODEL_SERVICES = {
    "gemini": gemini_service,
    "deepseek": deepseek_service,
    "grok": grok_service,
}

_SUBJECT_CONTEXT = {
    "math": "Focus: Mathematics. Provide step-by-step solutions with clear working.",
    "science": "Focus: Science (Physics, Chemistry, Biology). Use diagrams described in text when helpful.",
    "history": "Focus: History. Include Bangladeshi and South Asian historical context where relevant.",
    "literature": "Focus: Literature. Cover both Bangla literature (Tagore, Nazrul, Jibanananda) and English literature.",
    "general": "Focus: General knowledge and study skills.",
}


@router.post(
    "/",
    response_model=AIResponse,
    summary="Get subject-specific AI tutoring",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(ANONYMOUS_LIMIT)
async def study_help(request: Request, body: StudyRequest):
    """
    Ask a study question and receive expert AI tutoring.

    - **question**: Your study question
    - **subject**: `math`, `science`, `history`, `literature`, or `general`
    - **model**: AI model to use
    """
    service = _MODEL_SERVICES.get(body.model)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model '{body.model}'.",
        )

    clean_question = preprocess_bengali_text(body.question)
    detected_lang = detect_language(clean_question)
    lang_instruction = build_language_instruction("auto", detected_lang)

    subject_context = _SUBJECT_CONTEXT.get(body.subject, _SUBJECT_CONTEXT["general"])
    system_prompt = STUDY_HELPER_PROMPT + f"\n\n{subject_context}" + lang_instruction

    try:
        reply = await service.generate_response(
            prompt=clean_question,
            system_prompt=system_prompt,
            history=None,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {exc}",
        ) from exc

    return AIResponse(model=body.model, content=reply)
