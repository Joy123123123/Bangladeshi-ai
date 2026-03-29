"""
Admission Prep Endpoint

Provides targeted preparation for BUET, DU, Medical, BCS, SSC, and HSC
admission/board examinations.
"""

import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import AdmissionRequest, ExamType
from app.services.banglish_parser import banglish_parser
from app.services.nctb_context_service import nctb_service
from app.services.rag_service import rag_service
from app.services.ai_router import ai_router
from app.services.admission_engine import admission_engine
from app.core.config import settings
from app.utils.validators import validate_message, sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter()


async def _admission_stream(
    request: AdmissionRequest,
    session_id: str,
) -> AsyncGenerator[bytes, None]:
    """Generate admission prep response as an SSE stream."""
    try:
        sanitized = sanitize_text(request.question)
        parse_result = await banglish_parser.full_parse(sanitized)
        normalized_question = parse_result["normalized"]

        # Build exam-specific system prompt
        system_prompt = await nctb_service.get_context_prompt(
            subject=request.subject,
            exam_type=request.exam_type,
            data_saver_mode=request.data_saver_mode,
        )

        # Add admission strategy context
        strategy = admission_engine.get_exam_strategy(request.exam_type.value)
        if strategy:
            system_prompt += f"\n\n{strategy}"

        # Query RAG
        rag_context = await rag_service.query(
            query=normalized_question,
            subject=request.subject.value if request.subject else None,
            exam_type=request.exam_type.value,
        )

        # Get shortcuts for the topic
        shortcuts = admission_engine.get_shortcuts_for_topic(normalized_question)
        if shortcuts:
            shortcuts_text = "\n".join(f"• {s}" for s in shortcuts)
            system_prompt += f"\n\n**প্রাসঙ্গিক শর্টকাট:**\n{shortcuts_text}"

        chunk_size = settings.CHUNK_SIZE // 2 if request.data_saver_mode else settings.CHUNK_SIZE
        chunk_buffer = ""

        async for text_chunk in ai_router.route(
            message=normalized_question,
            system_prompt=system_prompt,
            rag_context=rag_context,
            preferred_model=request.preferred_model,
        ):
            chunk_buffer += text_chunk
            while len(chunk_buffer) >= chunk_size:
                emit, chunk_buffer = chunk_buffer[:chunk_size], chunk_buffer[chunk_size:]
                payload = json.dumps({"content": emit, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n".encode("utf-8")

        if chunk_buffer:
            payload = json.dumps({"content": chunk_buffer, "done": False}, ensure_ascii=False)
            yield f"data: {payload}\n\n".encode("utf-8")

        yield b"data: [DONE]\n\n"

    except Exception as exc:
        logger.error("Admission stream error for session %s: %s", session_id, exc)
        error_payload = json.dumps(
            {"content": "", "done": True, "error": str(exc)},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n".encode("utf-8")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/admission/stream", tags=["admission"], summary="Streaming admission prep")
async def admission_stream(request: AdmissionRequest) -> StreamingResponse:
    """
    SSE streaming endpoint for admission exam preparation.

    Provides:
    - Question-solving with step-by-step explanation
    - Exam-specific tips and strategies
    - Previous-year question patterns (via RAG)
    - Time-saving shortcuts
    """
    is_valid, error = validate_message(request.question)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    session_id = str(uuid.uuid4())
    logger.info("Admission stream | exam=%s | subject=%s", request.exam_type, request.subject)

    return StreamingResponse(
        _admission_stream(request, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-ID": session_id,
        },
    )


@router.get("/admission/strategy/{exam_type}", tags=["admission"], summary="Get exam strategy")
async def get_exam_strategy(exam_type: str):
    """Return preparation strategy for a given admission exam."""
    exam_type_upper = exam_type.upper()

    valid_types = [e.value for e in ExamType]
    matched = next((e for e in valid_types if e.upper() == exam_type_upper), None)
    if not matched:
        raise HTTPException(
            status_code=404,
            detail=f"Exam type '{exam_type}' not found. Valid types: {valid_types}",
        )

    strategy = admission_engine.get_exam_strategy(matched)
    marks = admission_engine.get_marks_breakdown(matched)

    return {
        "exam_type": matched,
        "strategy": strategy,
        "marks_breakdown": marks,
    }


@router.get("/admission/exams", tags=["admission"], summary="List available exam types")
async def list_exam_types():
    """Return all supported admission exam types."""
    from app.core.constants import ADMISSION_EXAMS
    return {
        "exams": [
            {"code": code, "name_bn": name_bn}
            for code, name_bn in ADMISSION_EXAMS.items()
        ]
    }
